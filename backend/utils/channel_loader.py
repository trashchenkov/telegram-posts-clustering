from typing import List
import os
import logging

logger = logging.getLogger(__name__)

def load_channels_from_file(file_path: str = "config/channels.txt") -> List[str]:
    """Загружает список каналов из файла"""
    channels = []
    
    try:
        # Проверяем существование файла
        if not os.path.exists(file_path):
            logger.warning(f"Файл каналов {file_path} не найден")
            return []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                channel = line.strip()
                # Пропускаем пустые строки и комментарии
                if channel and not channel.startswith('#'):
                    # Убираем @ если есть
                    if channel.startswith('@'):
                        channel = channel[1:]
                    channels.append(channel)
        
        logger.info(f"Загружено {len(channels)} каналов из {file_path}")
        return channels
        
    except Exception as e:
        logger.error(f"Ошибка при загрузке каналов из {file_path}: {str(e)}")
        return []

def save_channels_to_file(channels: List[str], file_path: str = "config/channels.txt") -> bool:
    """Сохраняет список каналов в файл"""
    try:
        # Создаем директорию если не существует
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            for channel in channels:
                # Убираем @ если есть
                if channel.startswith('@'):
                    channel = channel[1:]
                f.write(f"{channel}\n")
        
        logger.info(f"Сохранено {len(channels)} каналов в {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка при сохранении каналов в {file_path}: {str(e)}")
        return False 