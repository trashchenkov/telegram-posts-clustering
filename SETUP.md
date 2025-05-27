# 🚀 Настройка и запуск проекта

Этот проект состоит из двух частей:
- **Frontend**: React + TypeScript (существующий UI)
- **Backend**: Python + FastAPI (новый API с реальным парсингом)

## 📋 Требования

- **Python 3.12+** (рекомендуется для лучшей совместимости с зависимостями)
- **Node.js 16+**
- **npm или yarn**

## 🔧 Настройка Backend

### 1. Переход в директорию backend
```bash
cd backend
```

### 2. Создание виртуального окружения
```bash
# Рекомендуется использовать Python 3.12 для лучшей совместимости
python3.12 -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Установка зависимостей
```bash
# Зависимости настроены без фиксированных версий для совместимости с разными Python
pip install -r requirements.txt
```

### 4. Настройка конфигурации
```bash
cp env.example .env
```

Отредактируйте `.env` файл:
```env
# Выберите LLM провайдера
LLM_PROVIDER=openai  # или anthropic, gemini, ollama, none

# Добавьте API ключ (один из них)
OPENAI_API_KEY=sk-your-key-here
# ANTHROPIC_API_KEY=sk-ant-your-key-here  
# GEMINI_API_KEY=your-key-here
```

### 5. Запуск backend
```bash
python main.py
```

Backend будет доступен на: http://localhost:8000
- API документация: http://localhost:8000/docs

## 🎨 Настройка Frontend

### 1. Переход в корневую директорию
```bash
cd ..  # из backend в корень проекта
```

### 2. Установка зависимостей
```bash
npm install
```

### 3. Запуск frontend
```bash
npm run dev
```

Frontend будет доступен на: http://localhost:5173

## 🔄 Режимы работы

### 1. С Backend (рекомендуется)
- Запустите backend (порт 8000)
- Запустите frontend (порт 5173)
- Frontend автоматически будет использовать backend API

### 2. Только Frontend (fallback)
- Запустите только frontend
- Будут использоваться mock данные

## 🤖 LLM Провайдеры

### OpenAI
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-3.5-turbo
```

### Anthropic Claude
```env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-haiku-20240307
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

Для Ollama сначала установите и запустите:
```bash
# Установка Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Загрузка модели
ollama pull llama2

# Запуск сервера
ollama serve
```

### Без кластеризации
```env
LLM_PROVIDER=none
```

## 📁 Структура проекта

```
проект/
├── backend/                 # Python API
│   ├── api/routes.py       # FastAPI роуты
│   ├── services/           # Парсинг и кластеризация
│   ├── models/             # Pydantic модели
│   ├── config/             # Настройки и каналы
│   └── main.py            # Точка входа
├── services/               # Frontend сервисы
├── components/             # React компоненты
├── App.tsx                # Главный компонент
└── package.json           # Frontend зависимости
```

## 🔍 Проверка работы

### 1. Backend Health Check
```bash
curl http://localhost:8000/api/v1/health
```

### 2. Список каналов
```bash
curl http://localhost:8000/api/v1/channels
```

### 3. Получение постов
```bash
curl -X POST http://localhost:8000/api/v1/posts \
  -H "Content-Type: application/json" \
  -d '{"channels": ["seeallochnaya"], "hours_back": 24}'
```

## 🚨 Возможные проблемы

### Backend не запускается
- Проверьте Python версию: `python --version`
- Активируйте виртуальное окружение
- Установите зависимости: `pip install -r requirements.txt`

### Ошибки парсинга Telegram
- snscrape может быть заблокирован при частых запросах
- Попробуйте уменьшить количество каналов
- Проверьте интернет соединение

### LLM не работает
- Проверьте API ключ в `.env`
- Убедитесь что провайдер настроен правильно
- Попробуйте `LLM_PROVIDER=none` для отключения

### CORS ошибки
- Убедитесь что backend запущен на порту 8000
- Проверьте настройки CORS в `backend/config/settings.py`

### Проблемы с зависимостями
- **Python версия**: Рекомендуется Python 3.12+ для лучшей совместимости
- **Конфликты версий**: Зависимости настроены без фиксированных версий
- **telethon удален**: Больше не используется, парсинг через HTTP и snscrape
- **Пересоздание venv**: При проблемах удалите `venv/` и создайте заново

## 📊 Мониторинг

### Логи Backend
Backend выводит подробные логи:
- Процесс парсинга каналов
- Время обработки
- Ошибки кластеризации
- Статистику по постам

### Логи Frontend
Откройте Developer Tools в браузере для просмотра:
- Запросы к backend
- Fallback на mock данные
- Ошибки кластеризации

## 🔧 Кастомизация

### Добавление каналов
Отредактируйте `backend/config/channels.txt`:
```
новый_канал
еще_один_канал
```

### Изменение настроек парсинга
В `backend/.env`:
```env
POSTS_LIMIT_PER_CHANNEL=100  # больше постов
HOURS_BACK=48               # за 48 часов
MAX_CONCURRENT_REQUESTS=10  # больше параллельных запросов
```

### Настройка кластеризации
В `backend/services/clustering_service.py` можно изменить:
- System prompt для LLM
- Логику обработки ошибок
- Количество категорий 