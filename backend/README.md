# Telegram Posts Aggregator - Backend

Python backend для агрегации и кластеризации постов из Telegram каналов с гибридной кластеризацией на основе embeddings и автоматическим определением оптимального количества кластеров.

## 🚀 Возможности

- **Реальный парсинг Telegram** через HTTP и snscrape (без API ключей)
- **Гибридная кластеризация**: sentence-transformers + K-means + LLM naming
- **Автоматическое определение** оптимального количества кластеров (2-8)
- **Множественные LLM провайдеры**: OpenAI, Anthropic, Google Gemini, Ollama
- **Асинхронная обработка** с ограничением concurrent запросов
- **Гибкая конфигурация** через файлы и переменные окружения
- **REST API** с автодокументацией
- **CORS поддержка** для фронтенда

## 🧠 Алгоритм кластеризации

### Гибридный подход
1. **Embeddings**: sentence-transformers/all-MiniLM-L6-v2 для семантического понимания
2. **Автоматическое k**: silhouette score для определения оптимального количества кластеров
3. **K-means**: кластеризация embeddings с оптимальным k
4. **LLM naming**: умные названия кластеров через OpenAI/Anthropic/Gemini
5. **Fallback**: keyword-based кластеризация при недоступности моделей

### Определение количества кластеров
```python
def _find_optimal_clusters(self, embeddings, min_clusters=2, max_clusters=8):
    # Перебираем k от 2 до 8
    # Используем silhouette_score для оценки качества
    # Выбираем k с лучшим score
```

## 📦 Установка и запуск

### 1. Создание виртуального окружения
```bash
python -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
```

### 2. Установка зависимостей
```bash
pip install -r requirements.txt
```

**Основные зависимости:**
- `sentence-transformers==4.1.0` - для embeddings
- `scikit-learn==1.3.2` - для K-means и silhouette score
- `openai==1.82.0` - для LLM naming
- `torch==2.7.0` - для sentence-transformers
- `numpy==1.26.4` - для математических операций

### 3. Настройка окружения
Скопируйте `env.example` в `.env` и настройте переменные:
```bash
cp env.example .env
```

### 4. Запуск сервера
```bash
source venv/bin/activate
python main.py
```

## 📦 Установка

1. **Создайте виртуальное окружение:**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows
```

2. **Установите зависимости:**
```bash
pip install -r requirements.txt
```

3. **Настройте конфигурацию:**
```bash
cp env.example .env
# Отредактируйте .env файл
```

## ⚙️ Конфигурация

### Переменные окружения (.env)

```env
# LLM Provider для названий кластеров
LLM_PROVIDER=openai  # openai, anthropic, gemini, ollama, none

# API Keys (выберите нужный)
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4.1-nano-2025-04-14

ANTHROPIC_API_KEY=your_key_here  
ANTHROPIC_MODEL=claude-3-haiku-20240307

GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-pro

# Настройки кластеризации
MIN_CLUSTERS=2
MAX_CLUSTERS=8

# Настройки парсинга
POSTS_LIMIT_PER_CHANNEL=50
HOURS_BACK=24
```

### Список каналов (config/channels.txt)

Один канал на строку, без символа @:
```
seeallochnaya
data_secrets
tsingular
```

## 🏃 Запуск

```bash
# Из директории backend
python main.py
```

API будет доступно по адресу: http://localhost:8000

- **Документация**: http://localhost:8000/docs
- **Health check**: http://localhost:8000/api/v1/health

## 📡 API Endpoints

### GET /api/v1/health
Проверка состояния сервиса
```json
{
  "status": "ok",
  "llm_provider": "openai",
  "llm_available": true,
  "channels_count": 49
}
```

### POST /api/v1/posts
Получение и кластеризация постов
```json
{
  "channels": ["seeallochnaya", "data_secrets"],
  "hours_back": 24
}
```

**Ответ:**
```json
{
  "posts": [
    {
      "id": "seeallochnaya_1234567890_http_0",
      "channelName": "seeallochnaya",
      "publicationDateTime": "2024-01-15T10:30:00",
      "postLink": "https://t.me/seeallochnaya/123",
      "postText": "Новая модель от OpenAI...",
      "hasMedia": false,
      "clusterName": "AI модели и разработка"
    }
  ],
  "total_count": 10,
  "processing_time_seconds": 2.55,
  "clusters_created": 2
}
```

### GET /api/v1/channels
Список отслеживаемых каналов

### GET /api/v1/providers
Информация о доступных LLM провайдерах

## 🔧 LLM Провайдеры

### OpenAI
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4.1-nano-2025-04-14
```

### Anthropic Claude
```env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-sonnet-20240229
```

### Google Gemini
```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=...
GEMINI_MODEL=gemini-pro
```

### Ollama (локальные модели)
```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

### Без LLM (только embeddings)
```env
LLM_PROVIDER=none
```

## 🏗️ Архитектура

```
backend/
├── api/
│   └── routes.py          # FastAPI роуты
├── config/
│   ├── settings.py        # Конфигурация
│   └── channels.txt       # Список каналов
├── models/
│   └── post.py           # Pydantic модели
├── services/
│   ├── telegram_parser.py # HTTP + snscrape парсинг
│   └── clustering_service.py # Гибридная кластеризация
├── utils/
│   └── channel_loader.py  # Утилиты для каналов
└── main.py               # Точка входа
```

## 🔍 Логирование

Все операции логируются с уровнем INFO. Логи включают:
- Процесс парсинга каналов
- Загрузка embedding модели
- Определение оптимального количества кластеров
- Время обработки кластеризации
- Генерация названий кластеров через LLM
- Статистику по постам

Пример логов:
```
🔄 Загружаем модель для embeddings...
✅ Embedding модель загружена
🔄 Получаем embeddings для 10 текстов...
✅ Embeddings получены: (10, 384)
🎯 Оптимальное количество кластеров: 2 (score: 0.342)
✅ Кластеризация завершена: 2 кластеров
🤖 Запрашиваем названия кластеров у LLM...
✅ LLM сгенерировал названия: {0: "AI видео и звук", 1: "Технологии и игры"}
```

## 🚨 Ограничения

- **sentence-transformers**: Требует ~1GB RAM для модели
- **snscrape**: Может быть заблокирован Telegram при частых запросах
- **Rate limits**: LLM провайдеры имеют лимиты запросов
- **Processing time**: Зависит от количества постов и LLM провайдера
- **Concurrent requests**: Настраивается через MAX_CONCURRENT_REQUESTS

## 🔄 Интеграция с фронтендом

Backend совместим с существующим React фронтендом. Нужно только изменить URL в `services/postService.ts`:

```typescript
const API_BASE_URL = 'http://localhost:8000/api/v1';
```

## Архитектура

- **HTTP парсер** - парсинг Telegram каналов через t.me/s/
- **Гибридная кластеризация** - embeddings + LLM для именования
- **Fallback система** - keyword-based кластеризация при отсутствии моделей

## API

- `GET /api/v1/health` - проверка состояния
- `POST /api/v1/posts` - получение и кластеризация постов

## Зависимости

- **FastAPI** - веб-фреймворк
- **sentence-transformers** - embeddings для кластеризации  
- **scikit-learn** - алгоритмы кластеризации
- **OpenAI** - LLM для именования кластеров
- **httpx + BeautifulSoup** - парсинг Telegram 