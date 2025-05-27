from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
import time
import logging

from models.post import PostsRequest, PostsResponse, ClusteringRequest, HealthResponse, Post
from services.telegram_parser import TelegramParser
from services.clustering_service import ClusteringService
from utils.channel_loader import load_channels_from_file
from config.settings import settings

logger = logging.getLogger(__name__)

router = APIRouter()

# Инициализируем сервисы
telegram_parser = TelegramParser()
clustering_service = ClusteringService()

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Проверка состояния API"""
    channels = load_channels_from_file()
    
    return HealthResponse(
        status="ok",
        llm_provider=settings.llm_provider,
        llm_available=clustering_service.is_available(),
        channels_count=len(channels)
    )

@router.get("/channels")
async def get_channels():
    """Получить список отслеживаемых каналов"""
    channels = load_channels_from_file()
    return {"channels": channels, "count": len(channels)}

@router.post("/posts", response_model=PostsResponse)
async def get_posts(request: PostsRequest = None):
    """Получить и кластеризовать посты"""
    start_time = time.time()
    
    try:
        # Если каналы не переданы в запросе, загружаем из файла
        if request is None or not request.channels:
            channels = load_channels_from_file()
            hours_back = 24
        else:
            channels = request.channels
            hours_back = request.hours_back
        
        if not channels:
            raise HTTPException(status_code=400, detail="Список каналов пуст")
        
        logger.info(f"Запрос на получение постов из {len(channels)} каналов за последние {hours_back} часов")
        
        # Парсим посты
        raw_posts = await telegram_parser.parse_channels(
            channels=channels,
            hours_back=hours_back,
            limit=settings.posts_limit_per_channel
        )
        
        if not raw_posts:
            logger.warning("Посты не найдены")
            return PostsResponse(
                posts=[],
                total_count=0,
                channels_processed=len(channels),
                processing_time_seconds=time.time() - start_time
            )
        
        # Кластеризуем посты
        clustered_posts = await clustering_service.cluster_posts(raw_posts)
        
        processing_time = time.time() - start_time
        logger.info(f"Обработка завершена за {processing_time:.2f} секунд")
        
        return PostsResponse(
            posts=clustered_posts,
            total_count=len(clustered_posts),
            channels_processed=len(channels),
            processing_time_seconds=processing_time
        )
        
    except Exception as e:
        logger.error(f"Ошибка при получении постов: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")

@router.post("/cluster", response_model=List[Post])
async def cluster_posts(request: ClusteringRequest):
    """Кластеризовать уже полученные посты"""
    try:
        logger.info(f"Запрос на кластеризацию {len(request.posts)} постов")
        
        # Если указан провайдер, временно переключаемся на него
        original_provider = settings.llm_provider
        if request.provider and request.provider != settings.llm_provider:
            settings.llm_provider = request.provider
            # Переинициализируем сервис кластеризации
            global clustering_service
            clustering_service = ClusteringService()
        
        try:
            clustered_posts = await clustering_service.cluster_posts(request.posts)
            return clustered_posts
        finally:
            # Возвращаем оригинальный провайдер
            if request.provider and request.provider != original_provider:
                settings.llm_provider = original_provider
                clustering_service = ClusteringService()
        
    except Exception as e:
        logger.error(f"Ошибка при кластеризации: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка кластеризации: {str(e)}")

@router.get("/providers")
async def get_providers():
    """Получить информацию о доступных LLM провайдерах"""
    providers = {
        "current": clustering_service.get_provider_info(),
        "available": [
            {
                "name": "openai",
                "models": ["gpt-4", "gpt-3.5-turbo"],
                "configured": bool(settings.openai_api_key)
            },
            {
                "name": "anthropic", 
                "models": ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"],
                "configured": bool(settings.anthropic_api_key)
            },
            {
                "name": "gemini",
                "models": ["gemini-pro", "gemini-pro-vision"],
                "configured": bool(settings.gemini_api_key)
            },
            {
                "name": "ollama",
                "models": ["llama2", "mistral", "codellama"],
                "configured": True  # Ollama не требует API ключа
            },
            {
                "name": "none",
                "models": [],
                "configured": True
            }
        ]
    }
    return providers 