# 📱 Telegram Posts Aggregator

Приложение для агрегации и кластеризации постов из Telegram каналов с поддержкой различных LLM провайдеров и автоматическим определением оптимального количества кластеров.

## ✨ Возможности

- 🔍 **Реальный парсинг Telegram** через HTTP и snscrape (без API ключей)
- 🤖 **Гибридная кластеризация** с embeddings + LLM для названий кластеров
- 🎯 **Автоматическое определение** оптимального количества кластеров (silhouette score)
- 🧠 **Поддержка LLM**: OpenAI GPT-4, Anthropic Claude, Google Gemini, Ollama
- 📊 **Модели embeddings**: sentence-transformers (all-MiniLM-L6-v2)
- ⚡ **Асинхронная обработка** с ограничением concurrent запросов
- 🎨 **Современный UI** на React + TypeScript
- 🔧 **Гибкая конфигурация** через файлы и переменные окружения
- 📊 **REST API** с автодокументацией

## 🧠 Алгоритм кластеризации

### Автоматическое определение количества кластеров
Система автоматически определяет оптимальное количество кластеров (от 2 до 8) используя:
- **K-means кластеризацию** на embeddings
- **Silhouette score** для оценки качества кластеризации
- **Перебор значений k** с выбором лучшего результата

### Гибридный подход
1. **Embeddings**: sentence-transformers для семантического понимания
2. **K-means**: автоматическая кластеризация с оптимальным k
3. **LLM naming**: умные названия кластеров вместо "Кластер 1, 2, 3..."
4. **Fallback**: keyword-based кластеризация при недоступности моделей

## 🤖 Поддерживаемые модели

### LLM для названий кластеров
| Провайдер | Модели | Настройка |
|-----------|--------|-----------|
| **OpenAI** | gpt-4, gpt-4-turbo, gpt-3.5-turbo | `OPENAI_API_KEY` |
| **Anthropic** | claude-3-opus, claude-3-sonnet, claude-3-haiku | `ANTHROPIC_API_KEY` |
| **Google** | gemini-pro, gemini-1.5-pro | `GEMINI_API_KEY` |
| **Ollama** | llama2, mistral, codellama | Локально |

### Embeddings модели
- **sentence-transformers/all-MiniLM-L6-v2** (по умолчанию)
- Автоматическая загрузка при первом запуске
- Работает локально без API ключей

## 🚀 Быстрый старт

### Автоматический запуск (Linux/Mac)
```bash
./start.sh
```

### Ручной запуск

1. **Backend (Python)**:
```bash
cd backend
python3.12 -m venv venv  # Используйте Python 3.12 для лучшей совместимости
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt  # Зависимости без фиксированных версий
cp env.example .env
# Отредактируйте .env (добавьте API ключ для LLM)
python main.py
```

2. **Frontend (React)**:
```bash
npm install
npm run dev
```

## 🌐 Доступ

- **Frontend UI**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🏗️ Архитектура

```
📁 Проект
├── 🐍 backend/              # Python FastAPI
│   ├── api/                 # REST API роуты
│   ├── services/            # Парсинг и кластеризация
│   │   ├── telegram_parser.py    # HTTP + snscrape парсинг
│   │   └── clustering_service.py # Гибридная кластеризация
│   ├── models/              # Pydantic модели
│   └── config/              # Настройки и каналы
├── ⚛️ components/           # React компоненты
├── 🔧 services/             # Frontend сервисы
└── 📱 App.tsx              # Главный компонент
```

## 📋 Требования

- **Python 3.12+** (рекомендуется для лучшей совместимости)
- **Node.js 16+**
- **API ключ LLM** (опционально, для умных названий кластеров)
- **4GB RAM** (для sentence-transformers модели)

## 🔧 Конфигурация

### Backend (.env)
```env
# LLM для названий кластеров
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key
OPENAI_MODEL=gpt-4

# Настройки парсинга
POSTS_LIMIT_PER_CHANNEL=50
HOURS_BACK=24

# Настройки кластеризации
MIN_CLUSTERS=2
MAX_CLUSTERS=8
```

### Каналы (backend/config/channels.txt)
```
seeallochnaya
data_secrets
tsingular
```

## 🎯 Использование

1. **Запустите** оба сервиса
2. **Откройте** http://localhost:5173
3. **Нажмите** "Загрузить и кластеризовать посты"
4. **Просматривайте** результаты с умными названиями кластеров

## 🔄 Режимы работы

- **Полный режим**: HTTP парсинг + embeddings + LLM названия
- **Без LLM**: HTTP парсинг + embeddings + простые названия
- **Fallback**: Keyword-based кластеризация
- **Mock режим**: Тестовые данные (если backend недоступен)

## 🚨 Ограничения

- **Rate limits**: LLM провайдеры имеют лимиты
- **Telegram blocking**: HTTP парсинг может блокироваться
- **Memory usage**: sentence-transformers требует ~1GB RAM
- **Processing time**: Зависит от количества постов и LLM провайдера

## 📖 Документация

- [📚 Подробная настройка](SETUP.md)
- [🤖 Настройка моделей](MODELS.md)
- [🐍 Backend документация](backend/README.md)
- [📡 API Reference](http://localhost:8000/docs)

## 🤝 Вклад в проект

1. Fork репозитория
2. Создайте feature branch
3. Внесите изменения
4. Создайте Pull Request

## 📄 Лицензия

MIT License - см. [LICENSE](LICENSE) файл.

---

**Создано с ❤️ для агрегации Telegram контента**
