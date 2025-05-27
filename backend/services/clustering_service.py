from typing import List, Optional, Dict, Any
import asyncio
import logging
import random
import json
from datetime import datetime
import numpy as np
from sklearn.cluster import DBSCAN, KMeans
from sklearn.metrics import silhouette_score
from sentence_transformers import SentenceTransformer
import openai

from models.post import RawPost, Post
from config.settings import settings

logger = logging.getLogger(__name__)

class ClusteringService:
    def __init__(self):
        self.embedding_model = None
        self.openai_client = None
        
        # Простые категории для keyword-based кластеризации (fallback)
        self.keyword_clusters = {
            "Искусственный интеллект": ["ai", "ии", "нейро", "ml", "машинное обучение", "gpt", "llm", "openai", "anthropic", "claude"],
            "Вакансии": ["работа", "вакансия", "hiring", "job", "developer", "разработчик"],
            "Новости": ["новости", "news", "обновление", "релиз", "анонс"],
            "Мемы": ["мем", "😂", "🤣", "funny", "юмор", "прикол"],
            "Криптовалюты": ["крипто", "bitcoin", "блокчейн", "ethereum", "btc", "eth"],
            "Разработка": ["код", "программ", "разработ", "python", "javascript", "github"],
            "Бизнес": ["стартап", "бизнес", "инвест", "деньги", "финансы"],
            "Образование": ["курс", "обучение", "туториал", "урок", "лекция"],
            "События": ["конференция", "митап", "событие", "встреча", "мероприятие"]
        }
        
        self._initialize_models()

    def _initialize_models(self):
        """Инициализация моделей"""
        try:
            # Инициализация embedding модели
            logger.info("🔄 Загружаем модель для embeddings...")
            self.embedding_model = SentenceTransformer(settings.embedding_model)
            logger.info("✅ Embedding модель загружена")
            
            # Инициализация OpenAI клиента
            if settings.openai_api_key:
                self.openai_client = openai.OpenAI(api_key=settings.openai_api_key)
                logger.info("✅ OpenAI клиент инициализирован")
            else:
                logger.warning("⚠️ OpenAI API ключ не найден, будет использоваться fallback")
                
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации моделей: {e}")

    def _get_embeddings(self, texts: List[str]) -> np.ndarray:
        """Получение embeddings для текстов"""
        if not self.embedding_model:
            raise Exception("Embedding модель не инициализирована")
        
        # Фильтруем пустые тексты
        valid_texts = [text if text else "Пост без текста" for text in texts]
        
        logger.info(f"🔄 Получаем embeddings для {len(valid_texts)} текстов...")
        embeddings = self.embedding_model.encode(valid_texts)
        logger.info(f"✅ Embeddings получены: {embeddings.shape}")
        
        return embeddings

    def _find_optimal_clusters(self, embeddings: np.ndarray, min_clusters: int = None, max_clusters: int = None) -> int:
        """Определение оптимального количества кластеров"""
        if min_clusters is None:
            min_clusters = settings.min_clusters
        if max_clusters is None:
            max_clusters = settings.max_clusters
            
        if len(embeddings) < min_clusters:
            return 1
        
        best_score = -1
        best_k = min_clusters
        
        for k in range(min_clusters, min(max_clusters + 1, len(embeddings))):
            try:
                kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
                cluster_labels = kmeans.fit_predict(embeddings)
                
                if len(set(cluster_labels)) > 1:  # Больше одного кластера
                    score = silhouette_score(embeddings, cluster_labels)
                    if score > best_score:
                        best_score = score
                        best_k = k
            except Exception as e:
                logger.warning(f"Ошибка при k={k}: {e}")
                continue
        
        logger.info(f"🎯 Оптимальное количество кластеров: {best_k} (score: {best_score:.3f})")
        return best_k

    def _cluster_embeddings(self, embeddings: np.ndarray) -> np.ndarray:
        """Кластеризация embeddings"""
        if len(embeddings) < 2:
            return np.array([0] * len(embeddings))
        
        # Определяем оптимальное количество кластеров
        optimal_k = self._find_optimal_clusters(embeddings)
        
        # Выполняем кластеризацию
        if optimal_k == 1:
            return np.array([0] * len(embeddings))
        
        kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(embeddings)
        
        logger.info(f"✅ Кластеризация завершена: {optimal_k} кластеров")
        return cluster_labels

    def _get_representative_posts(self, posts: List[RawPost], cluster_labels: np.ndarray, embeddings: np.ndarray) -> Dict[int, List[str]]:
        """Получение репрезентативных постов для каждого кластера"""
        cluster_representatives = {}
        
        for cluster_id in set(cluster_labels):
            cluster_mask = cluster_labels == cluster_id
            cluster_posts = [posts[i] for i in range(len(posts)) if cluster_mask[i]]
            cluster_embeddings = embeddings[cluster_mask]
            
            # Берем до 3 самых репрезентативных постов
            if len(cluster_posts) <= 3:
                representatives = [post.post_text or "Пост без текста" for post in cluster_posts]
            else:
                # Находим центроид кластера
                centroid = np.mean(cluster_embeddings, axis=0)
                
                # Находим посты ближайшие к центроиду
                distances = np.linalg.norm(cluster_embeddings - centroid, axis=1)
                closest_indices = np.argsort(distances)[:3]
                
                representatives = [cluster_posts[i].post_text or "Пост без текста" for i in closest_indices]
            
            cluster_representatives[cluster_id] = representatives
        
        return cluster_representatives

    async def _generate_cluster_names_with_llm(self, cluster_representatives: Dict[int, List[str]]) -> Dict[int, str]:
        """Генерация названий кластеров с помощью LLM"""
        if not self.openai_client:
            logger.warning("⚠️ OpenAI недоступен, используем fallback названия")
            return {cluster_id: f"Кластер {cluster_id + 1}" for cluster_id in cluster_representatives.keys()}
        
        try:
            # Формируем промпт для всех кластеров сразу
            prompt = """Проанализируй группы постов из Telegram каналов про AI/технологии и дай каждой группе короткое название (2-4 слова).

Группы постов:
"""
            
            for cluster_id, posts in cluster_representatives.items():
                prompt += f"\nГруппа {cluster_id + 1}:\n"
                for i, post in enumerate(posts, 1):
                    prompt += f"{i}. {post[:200]}...\n"
            
            prompt += """
Ответь в формате JSON:
{
  "0": "Название для группы 1",
  "1": "Название для группы 2",
  ...
}

Названия должны быть на русском языке, короткие и отражать основную тему группы."""

            logger.info("🤖 Запрашиваем названия кластеров у LLM...")
            
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model=settings.openai_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Парсим JSON ответ
            try:
                cluster_names = json.loads(result_text)
                # Конвертируем ключи в int
                cluster_names = {int(k): v for k, v in cluster_names.items()}
                logger.info(f"✅ LLM сгенерировал названия: {cluster_names}")
                return cluster_names
            except json.JSONDecodeError:
                logger.error(f"❌ Не удалось распарсить JSON от LLM: {result_text}")
                return {cluster_id: f"Кластер {cluster_id + 1}" for cluster_id in cluster_representatives.keys()}
                
        except Exception as e:
            logger.error(f"❌ Ошибка при генерации названий кластеров: {e}")
            return {cluster_id: f"Кластер {cluster_id + 1}" for cluster_id in cluster_representatives.keys()}

    def _classify_post_by_keywords(self, post_text: Optional[str]) -> str:
        """Простая кластеризация по ключевым словам (fallback)"""
        if not post_text:
            return "Нет текста"
        
        text_lower = post_text.lower()
        
        # Ищем совпадения с ключевыми словами
        for cluster_name, keywords in self.keyword_clusters.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return cluster_name
        
        return "Некатегоризованные"

    async def cluster_posts(self, raw_posts: List[RawPost]) -> List[Post]:
        """Гибридная кластеризация постов"""
        logger.info(f"🚀 Начинаем гибридную кластеризацию {len(raw_posts)} постов...")
        start_time = datetime.now()
        
        if len(raw_posts) == 0:
            return []
        
        # Если постов мало или нет embedding модели, используем keyword-based
        if len(raw_posts) < 3 or not self.embedding_model:
            logger.info("🔄 Используем keyword-based кластеризацию (мало постов или нет модели)")
            clustered_posts = []
            for post in raw_posts:
                cluster_name = self._classify_post_by_keywords(post.post_text)
                clustered_post = Post(**post.dict(), cluster_name=cluster_name)
                clustered_posts.append(clustered_post)
            return clustered_posts
        
        try:
            # 1. Получаем embeddings
            texts = [post.post_text or "Пост без текста" for post in raw_posts]
            embeddings = self._get_embeddings(texts)
            
            # 2. Кластеризуем
            cluster_labels = self._cluster_embeddings(embeddings)
            
            # 3. Получаем репрезентативные посты
            cluster_representatives = self._get_representative_posts(raw_posts, cluster_labels, embeddings)
            
            # 4. Генерируем названия кластеров с помощью LLM
            cluster_names = await self._generate_cluster_names_with_llm(cluster_representatives)
            
            # 5. Присваиваем названия кластеров постам
            clustered_posts = []
            for i, post in enumerate(raw_posts):
                cluster_id = cluster_labels[i]
                cluster_name = cluster_names.get(cluster_id, f"Кластер {cluster_id + 1}")
                clustered_post = Post(**post.dict(), cluster_name=cluster_name)
                clustered_posts.append(clustered_post)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"✅ Гибридная кластеризация завершена за {processing_time:.2f} секунд")
            logger.info(f"📊 Создано кластеров: {len(set(cluster_labels))}")
            
            return clustered_posts
            
        except Exception as e:
            logger.error(f"❌ Ошибка в гибридной кластеризации: {e}")
            logger.info("🔄 Переключаемся на keyword-based кластеризацию")
            
            # Fallback на keyword-based
            clustered_posts = []
            for post in raw_posts:
                cluster_name = self._classify_post_by_keywords(post.post_text)
                clustered_post = Post(**post.dict(), cluster_name=cluster_name)
                clustered_posts.append(clustered_post)
            
            return clustered_posts

    def is_available(self) -> bool:
        """Проверка доступности сервиса кластеризации"""
        return True  # Всегда доступен благодаря fallback

    def get_provider_info(self) -> dict:
        """Информация о текущем провайдере"""
        has_embeddings = self.embedding_model is not None
        has_openai = self.openai_client is not None
        
        if has_embeddings and has_openai:
            provider = "hybrid (embeddings + LLM)"
        elif has_embeddings:
            provider = "embeddings only"
        else:
            provider = "keyword-based"
        
        return {
            "provider": provider,
            "available": True,
            "embedding_model": "all-MiniLM-L6-v2" if has_embeddings else None,
            "llm_model": settings.openai_model if has_openai else None
        } 