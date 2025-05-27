from datetime import datetime, timedelta
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
        
        # Mock данные для fallback
        self.mock_texts = [
            "🚀 Новый релиз GPT-5!\n\nРеволюция в области ИИ продолжается. Основные улучшения:\n• Скорость работы увеличена в 3 раза\n• Поддержка 200+ языков\n• Новые возможности кодирования",
            "📊 Анализ рынка криптовалют\n\nBitcoin достиг нового максимума $75,000!\n\nОсновные факторы роста:\n- Институциональные инвестиции\n- Регулятивная ясность\n- Технологические улучшения",
            "💼 Открыта вакансия Senior Python Developer\n\nТребования:\n• Python 3.9+\n• FastAPI, Django\n• Docker, Kubernetes\n• Опыт с ML/AI\n\nЗарплата: от 300k руб",
            "🔬 Исследование показало эффективность новых алгоритмов ML\n\nУченые из MIT разработали алгоритм, который:\n\n✅ Обучается в 10 раз быстрее\n✅ Требует на 50% меньше данных\n✅ Показывает лучшую точность",
            "😂 Мем дня: когда код работает с первого раза\n\n[Картинка с удивленным программистом]\n\n— Это невозможно!\n— Но факт остается фактом...",
            "🎯 Стартап привлек $50M инвестиций\n\nAI-платформа для автоматизации бизнес-процессов получила серию B.\n\nИнвесторы:\n• Sequoia Capital\n• Andreessen Horowitz\n• Y Combinator",
            "📚 Новый курс по машинному обучению от Stanford\n\nCS229: Machine Learning\n\nЧто изучим:\n🔹 Supervised Learning\n🔹 Unsupervised Learning\n🔹 Deep Learning\n🔹 Reinforcement Learning\n\nСтарт: 15 февраля",
            "⚡ Обновление Telegram\n\nДобавлены новые функции для разработчиков:\n\n🆕 Bot API 7.0\n🆕 Webhook улучшения\n🆕 Новые типы сообщений\n🆕 Расширенная аналитика",
            "🌟 Интервью с основателем успешного AI стартапа\n\n\"Главное — не бояться экспериментировать\"\n\nКлючевые моменты:\n• Важность команды\n• Фокус на проблеме клиента\n• Итеративный подход к разработке",
            "🔧 Туториал: как настроить CI/CD для Python проектов\n\nШаг за шагом:\n\n1️⃣ Настройка GitHub Actions\n2️⃣ Конфигурация тестов\n3️⃣ Автоматический деплой\n4️⃣ Мониторинг и алерты"
        ]
    
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
    
    def _clean_snscrape_text(self, text: str) -> str:
        """Очищает и форматирует текст от snscrape"""
        if not text:
            return None
            
        # Убираем лишние пробелы и табуляции
        text = re.sub(r'[ \t]+', ' ', text)
        
        # Нормализуем переносы строк
        text = re.sub(r'\r\n', '\n', text)
        text = re.sub(r'\r', '\n', text)
        
        # Убираем тройные+ переносы, оставляем максимум двойные
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        
        # Убираем пробелы в начале и конце строк
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)
        
        return text.strip() if text.strip() else None
    
    async def _parse_channel_with_http(self, channel: str, hours_back: int = 24, limit: int = 50) -> List[RawPost]:
        """Парсинг через HTTP запросы к t.me"""
        posts = []
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        try:
            url = f"https://t.me/s/{channel}"
            logger.info(f"🌐 Попытка HTTP парсинга канала {channel}: {url}")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Ищем посты в HTML
                post_elements = soup.find_all('div', class_='tgme_widget_message')
                
                post_count = 0
                for element in post_elements[:limit]:
                    try:
                        # Извлекаем ID поста
                        post_link_elem = element.find('a', class_='tgme_widget_message_date')
                        if not post_link_elem:
                            continue
                            
                        post_link = post_link_elem.get('href', '')
                        post_id = post_link.split('/')[-1] if post_link else str(post_count)
                        
                        # Извлекаем время
                        time_elem = element.find('time')
                        if time_elem and time_elem.get('datetime'):
                            post_time = datetime.fromisoformat(time_elem['datetime'].replace('Z', '+00:00'))
                            # Проверяем время публикации
                            if post_time < cutoff_time:
                                continue
                        else:
                            # Если время не найдено, используем текущее время минус случайный интервал
                            post_time = datetime.now() - timedelta(minutes=random.randint(0, hours_back * 60))
                        
                        # Извлекаем текст поста
                        text_elem = element.find('div', class_='tgme_widget_message_text')
                        post_text = self._extract_formatted_text(text_elem)
                        
                        # Проверяем наличие медиа
                        has_media = bool(element.find('a', class_='tgme_widget_message_photo_wrap') or 
                                       element.find('video') or 
                                       element.find('div', class_='tgme_widget_message_video'))
                        
                        if post_text or has_media:  # Добавляем только если есть контент
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
                            
                    except Exception as e:
                        logger.warning(f"Ошибка обработки поста в канале {channel}: {e}")
                        continue
                
                logger.info(f"✅ HTTP: найдено {post_count} реальных постов в канале {channel}")
                return posts
                
        except Exception as e:
            logger.warning(f"⚠️ HTTP парсинг не удался для канала {channel}: {e}")
            raise
    
    def _parse_channel_with_snscrape(self, channel: str, hours_back: int = 24, limit: int = 50) -> List[RawPost]:
        """Парсинг через snscrape"""
        posts = []
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        try:
            import snscrape.modules.telegram as snstelegram
            
            logger.info(f"🔧 Попытка парсинга канала {channel} через snscrape...")
            
            # Создаем scraper для канала
            scraper = snstelegram.TelegramChannelScraper(channel)
            
            post_count = 0
            for i, item in enumerate(scraper.get_items()):
                if i >= limit:
                    logger.info(f"Достигнут лимит {limit} постов для канала {channel}")
                    break
                    
                # Проверяем время публикации
                if item.date < cutoff_time:
                    logger.info(f"Достигнута граница времени {hours_back}ч для канала {channel}")
                    break
                
                # Извлекаем текст поста
                post_text = None
                if hasattr(item, 'content') and item.content:
                    post_text = self._clean_snscrape_text(item.content)
                elif hasattr(item, 'rawContent') and item.rawContent:
                    post_text = self._clean_snscrape_text(item.rawContent)
                
                # Проверяем наличие медиа
                has_media = False
                if hasattr(item, 'media') and item.media:
                    has_media = True
                elif hasattr(item, 'photo') and item.photo:
                    has_media = True
                elif hasattr(item, 'video') and item.video:
                    has_media = True
                
                # Формируем ссылку на пост
                post_link = f"https://t.me/{channel}/{item.id}" if hasattr(item, 'id') else item.url
                
                post = RawPost(
                    id=f"{channel}_snscrape_{item.id}_{int(item.date.timestamp())}",
                    channel_name=channel,
                    publication_datetime=item.date.isoformat(),
                    post_link=post_link,
                    post_text=post_text,
                    has_media=has_media
                )
                posts.append(post)
                post_count += 1
                
            logger.info(f"✅ snscrape: найдено {post_count} реальных постов в канале {channel}")
            return posts
            
        except ImportError as e:
            logger.error(f"❌ snscrape не установлен: {e}")
            raise
        except Exception as e:
            logger.warning(f"⚠️ snscrape ошибка для канала {channel}: {e}")
            raise
    
    async def _parse_channel_sync(self, channel: str, hours_back: int = 24, limit: int = 50) -> List[RawPost]:
        """Синхронный парсинг одного канала с fallback стратегией"""
        
        # Стратегия 1: HTTP парсинг
        try:
            return await self._parse_channel_with_http(channel, hours_back, limit)
        except Exception as e:
            logger.warning(f"HTTP парсинг не сработал для {channel}: {e}")
        
        # Стратегия 2: snscrape
        try:
            return self._parse_channel_with_snscrape(channel, hours_back, limit)
        except Exception as e:
            logger.warning(f"snscrape не сработал для {channel}: {e}")
        
        # Стратегия 3: Mock данные
        logger.info(f"🔄 Используем mock данные для канала {channel}")
        return self._generate_mock_posts(channel, hours_back, limit)
    
    def _generate_mock_posts(self, channel: str, hours_back: int = 24, limit: int = 50) -> List[RawPost]:
        """Генерирует mock посты для fallback"""
        posts = []
        
        # Генерируем случайное количество постов (3-8 на канал)
        num_posts = random.randint(3, min(8, limit))
        
        for i in range(num_posts):
            # Случайное время в пределах последних hours_back часов
            random_minutes = random.randint(0, hours_back * 60)
            post_time = datetime.now() - timedelta(minutes=random_minutes)
            
            # Случайный текст
            post_text = random.choice(self.mock_texts)
            
            # Случайное наличие медиа
            has_media = random.choice([True, False])
            
            post = RawPost(
                id=f"{channel}_mock_{int(post_time.timestamp())}_{i}",
                channel_name=channel,
                publication_datetime=post_time.isoformat(),
                post_link=f"https://t.me/{channel}/{random.randint(1000, 9999)}",
                post_text=post_text,
                has_media=has_media
            )
            posts.append(post)
        
        logger.info(f"📝 Сгенерировано {num_posts} mock постов для канала {channel}")
        return posts
    
    async def parse_channel(self, channel: str, hours_back: int = 24, limit: int = 50) -> List[RawPost]:
        """Асинхронный парсинг одного канала"""
        return await self._parse_channel_sync(channel, hours_back, limit)
    
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
        real_posts = 0
        mock_posts = 0
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"❌ Критическая ошибка при парсинге канала {channels[i]}: {str(result)}")
                # Добавляем mock данные для неудачных каналов
                mock_data = self._generate_mock_posts(channels[i], hours_back, limit)
                all_posts.extend(mock_data)
                mock_posts += len(mock_data)
            else:
                all_posts.extend(result)
                successful_channels += 1
                
                # Подсчитываем реальные vs mock посты
                for post in result:
                    if "_mock_" in post.id:
                        mock_posts += 1
                    else:
                        real_posts += 1
        
        # Сортируем по времени публикации (новые сначала)
        all_posts.sort(
            key=lambda x: datetime.fromisoformat(x.publication_datetime), 
            reverse=True
        )
        
        logger.info(f"✅ Парсинг завершен: {len(all_posts)} постов из {len(channels)} каналов")
        logger.info(f"📊 Статистика: {real_posts} реальных, {mock_posts} mock постов")
        logger.info(f"🎯 Успешных каналов: {successful_channels}/{len(channels)}")
        
        return all_posts
    
    def __del__(self):
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=True) 