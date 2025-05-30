from datetime import datetime, timedelta, timezone
from typing import List, Optional
import logging
import asyncio
import random
from concurrent.futures import ThreadPoolExecutor
import re
import os
import httpx
from bs4 import BeautifulSoup

from models.post import RawPost

logger = logging.getLogger(__name__)

class TelegramParser:
    def __init__(self, max_workers: int = 5):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
    def _extract_formatted_text(self, text_elem) -> str:
        """Извлекает текст с сохранением базового форматирования"""
        if not text_elem:
            return None
            
        # Заменяем <br> на переносы строк
        for br in text_elem.find_all('br'):
            br.replace_with('\n')
        
        # Заменяем блочные элементы на переносы строк
        for block in text_elem.find_all(['div', 'p']):
            if block.get_text(strip=True):  # Только если есть текст
                block.insert_after('\n')
        
        # Получаем текст
        text = text_elem.get_text()
        
        # Очищаем лишние пробелы и переносы
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # Убираем тройные+ переносы
        text = re.sub(r'[ \t]+', ' ', text)  # Убираем лишние пробелы
        text = text.strip()
        
        return text if text else None
    
    async def _parse_channel_with_http(self, channel: str, hours_back: int = 24, limit: int = 50) -> List[RawPost]:
        """Парсинг через HTTP запросы к t.me"""
        posts = []
        # Используем UTC timezone для корректного сравнения
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours_back)
        logger.info(f"🕒 Фильтруем посты новее {cutoff_time.isoformat()} (последние {hours_back}ч)")
        
        try:
            url = f"https://t.me/s/{channel}"
            logger.info(f"🌐 Попытка HTTP парсинга канала {channel}: {url}")
            
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Ищем посты в HTML - пробуем разные селекторы
                post_elements = soup.find_all('div', class_='tgme_widget_message')
                
                # Если не найдены посты с классом tgme_widget_message, пробуем другие варианты
                if not post_elements:
                    # Возможно, структура изменилась, пробуем другие селекторы
                    post_elements = soup.find_all('div', class_='tgme_channel_post')
                    if not post_elements:
                        post_elements = soup.find_all('article')
                    if not post_elements:
                        post_elements = soup.find_all('div', class_='message')
                
                logger.info(f"🔍 Найдено {len(post_elements)} элементов постов в HTML")
                
                # Если постов все еще нет, возможно канал требует авторизации или изменил структуру
                if not post_elements:
                    logger.warning(f"⚠️ Посты не найдены на странице {response.url}. Возможно, канал требует авторизации или изменил структуру.")
                    # Проверяем, есть ли кнопка "View in Telegram" - это означает, что нужна авторизация
                    view_button = soup.find('a', class_='tgme_action_button_new')
                    if view_button:
                        logger.info(f"🔒 Канал {channel} требует авторизации в Telegram для просмотра постов")
                    return []
                
                post_count = 0
                skipped_old = 0
                skipped_no_time = 0
                skipped_no_content = 0
                
                for element in post_elements[:limit]:
                    try:
                        # Извлекаем ID поста - пробуем разные способы
                        post_link_elem = element.find('a', class_='tgme_widget_message_date')
                        if not post_link_elem:
                            # Пробуем другие селекторы для ссылки на пост
                            post_link_elem = element.find('a', href=True)
                        if not post_link_elem:
                            continue
                            
                        post_link = post_link_elem.get('href', '')
                        post_id = post_link.split('/')[-1] if post_link else str(post_count)
                        
                        # Извлекаем время - пробуем несколько способов
                        post_time = None
                        time_elem = element.find('time')
                        
                        if time_elem and time_elem.get('datetime'):
                            datetime_str = time_elem['datetime']
                            try:
                                # Обрабатываем разные форматы времени
                                if datetime_str.endswith('Z'):
                                    post_time = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
                                elif '+' in datetime_str or datetime_str.endswith('00'):
                                    post_time = datetime.fromisoformat(datetime_str)
                                else:
                                    # Если нет timezone info, считаем UTC
                                    post_time = datetime.fromisoformat(datetime_str).replace(tzinfo=timezone.utc)
                                    
                                logger.debug(f"📅 Пост {post_id}: время {post_time.isoformat()}")
                                
                            except Exception as e:
                                logger.warning(f"⚠️ Ошибка парсинга времени '{datetime_str}' для поста {post_id}: {e}")
                                post_time = None
                        
                        # Если время не найдено, пропускаем пост
                        if post_time is None:
                            logger.debug(f"⏰ Пост {post_id}: время не найдено, пропускаем")
                            skipped_no_time += 1
                            continue
                        
                        # Проверяем время публикации
                        if post_time < cutoff_time:
                            logger.debug(f"🕒 Пост {post_id}: слишком старый ({post_time.isoformat()}), пропускаем")
                            skipped_old += 1
                            continue
                        
                        # Извлекаем текст поста - пробуем разные селекторы
                        text_elem = element.find('div', class_='tgme_widget_message_text')
                        if not text_elem:
                            text_elem = element.find('div', class_='message_text')
                        if not text_elem:
                            text_elem = element.find('div', class_='post_content')
                        
                        post_text = self._extract_formatted_text(text_elem)
                        
                        # Проверяем наличие медиа - пробуем разные селекторы
                        has_media = bool(
                            element.find('a', class_='tgme_widget_message_photo_wrap') or 
                                       element.find('video') or 
                            element.find('div', class_='tgme_widget_message_video') or
                            element.find('img') or
                            element.find('div', class_='media')
                        )
                        
                        # Добавляем только если есть содержательный текст
                        # Медиа-посты без текста пропускаем, так как они не несут информационной ценности для кластеризации
                        if post_text and len(post_text.strip()) > 10:  # Минимум 10 символов содержательного текста
                            post = RawPost(
                                id=f"{channel}_http_{post_id}_{int(post_time.timestamp())}",
                                channel_name=channel,
                                publication_datetime=post_time.isoformat(),
                                post_link=post_link or f"https://t.me/{channel}/{post_id}",
                                post_text=post_text,
                                has_media=has_media
                            )
                            posts.append(post)
                            post_count += 1
                            logger.debug(f"✅ Пост {post_id}: добавлен ({post_time.isoformat()})")
                        else:
                            logger.debug(f"⏭️ Пост {post_id}: пропущен (нет содержательного текста)")
                            skipped_no_content += 1
                            
                    except Exception as e:
                        logger.warning(f"Ошибка обработки поста в канале {channel}: {e}")
                        continue
                
                logger.info(f"✅ HTTP: найдено {post_count} актуальных постов в канале {channel}")
                logger.info(f"📊 Статистика: пропущено старых: {skipped_old}, без времени: {skipped_no_time}, без содержательного текста: {skipped_no_content}")
                return posts
                
        except Exception as e:
            logger.warning(f"⚠️ HTTP парсинг не удался для канала {channel}: {e}")
            return []
    
    async def parse_channel(self, channel: str, hours_back: int = 24, limit: int = 50) -> List[RawPost]:
        """Асинхронный парсинг одного канала"""
        return await self._parse_channel_with_http(channel, hours_back, limit)
    
    async def parse_channels(self, channels: List[str], hours_back: int = 24, limit: int = 50) -> List[RawPost]:
        """Асинхронный парсинг нескольких каналов"""
        logger.info(f"🚀 Начинаем парсинг {len(channels)} каналов...")
        
        # Запускаем парсинг всех каналов параллельно
        tasks = [
            self.parse_channel(channel, hours_back, limit) 
            for channel in channels
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Собираем все посты
        all_posts = []
        successful_channels = 0
        failed_channels = 0
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"❌ Критическая ошибка при парсинге канала {channels[i]}: {str(result)}")
                failed_channels += 1
            elif len(result) == 0:
                logger.warning(f"⚠️ Канал {channels[i]} не содержит постов за указанный период")
                failed_channels += 1
            else:
                all_posts.extend(result)
                successful_channels += 1
                logger.info(f"✅ Канал {channels[i]}: получено {len(result)} постов")
        
        # Сортируем по времени публикации (новые сначала)
        all_posts.sort(
            key=lambda x: datetime.fromisoformat(x.publication_datetime), 
            reverse=True
        )
        
        logger.info(f"✅ Парсинг завершен: {len(all_posts)} реальных постов")
        logger.info(f"🎯 Успешных каналов: {successful_channels}/{len(channels)}")
        logger.info(f"❌ Неудачных каналов: {failed_channels}/{len(channels)}")
        
        return all_posts
    
    def __del__(self):
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=True) 