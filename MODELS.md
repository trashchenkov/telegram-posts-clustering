# 🤖 Настройка моделей для кластеризации

Подробное руководство по настройке различных моделей для умной кластеризации постов.

## 🧠 Архитектура кластеризации

Система использует **гибридный подход**:

1. **Embeddings модель** (sentence-transformers) - для семантического понимания текста
2. **K-means кластеризация** - автоматическое определение групп
3. **LLM модель** - для генерации умных названий кластеров

## 📊 Embeddings модели

### По умолчанию: all-MiniLM-L6-v2
```env
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

**Характеристики:**
- Размер: ~90MB
- Скорость: Быстрая
- Качество: Хорошее для общих задач
- Языки: Многоязычная (включая русский)

### Альтернативные модели

#### Для лучшего качества (медленнее):
```env
EMBEDDING_MODEL=all-mpnet-base-v2
```

#### Для русского языка:
```env
EMBEDDING_MODEL=sentence-transformers/LaBSE
```

#### Для быстрой работы (меньше качество):
```env
EMBEDDING_MODEL=all-MiniLM-L12-v2
```

## 🤖 LLM модели для названий кластеров

### OpenAI (рекомендуется)

#### GPT-4 (лучшее качество)
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4
```

#### GPT-4 Turbo (быстрее + дешевле)
```env
OPENAI_MODEL=gpt-4-turbo
```

#### GPT-3.5 Turbo (самый дешевый)
```env
OPENAI_MODEL=gpt-3.5-turbo
```

#### GPT-4.1 Nano (новая модель)
```env
OPENAI_MODEL=gpt-4.1-nano-2025-04-14
```

### Anthropic Claude

#### Claude 3 Opus (лучшее качество)
```env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-key-here
ANTHROPIC_MODEL=claude-3-opus-20240229
```

#### Claude 3 Sonnet (баланс цена/качество)
```env
ANTHROPIC_MODEL=claude-3-sonnet-20240229
```

#### Claude 3 Haiku (быстрый и дешевый)
```env
ANTHROPIC_MODEL=claude-3-haiku-20240307
```

### Google Gemini

#### Gemini Pro
```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your-gemini-key-here
GEMINI_MODEL=gemini-pro
```

#### Gemini 1.5 Pro
```env
GEMINI_MODEL=gemini-1.5-pro
```

### Ollama (локальные модели)

#### Llama 2
```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

#### Mistral
```env
OLLAMA_MODEL=mistral
```

#### CodeLlama
```env
OLLAMA_MODEL=codellama
```

**Установка Ollama:**
```bash
# macOS
brew install ollama

# Запуск сервера
ollama serve

# Загрузка модели
ollama pull llama2
```

## ⚙️ Настройки кластеризации

### Количество кластеров
```env
MIN_CLUSTERS=2    # Минимальное количество кластеров
MAX_CLUSTERS=8    # Максимальное количество кластеров
```

**Рекомендации:**
- Для 5-10 постов: `MIN_CLUSTERS=2, MAX_CLUSTERS=4`
- Для 10-50 постов: `MIN_CLUSTERS=2, MAX_CLUSTERS=8`
- Для 50+ постов: `MIN_CLUSTERS=3, MAX_CLUSTERS=10`

### Производительность
```env
MAX_CONCURRENT_REQUESTS=5    # Параллельные запросы к LLM
CLUSTERING_TIMEOUT=30        # Таймаут кластеризации (секунды)
```

## 🚀 Режимы работы

### 1. Полный режим (рекомендуется)
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key
EMBEDDING_MODEL=all-MiniLM-L6-v2
```
**Результат:** Семантическая кластеризация + умные названия

### 2. Только embeddings (без LLM)
```env
LLM_PROVIDER=none
EMBEDDING_MODEL=all-MiniLM-L6-v2
```
**Результат:** Семантическая кластеризация + простые названия ("Кластер 1", "Кластер 2")

### 3. Fallback режим
```env
LLM_PROVIDER=none
# Не устанавливать EMBEDDING_MODEL или указать несуществующую модель
```
**Результат:** Keyword-based кластеризация

## 💰 Стоимость использования

### OpenAI (примерные цены)
- **GPT-4**: ~$0.03 за 1K токенов
- **GPT-4 Turbo**: ~$0.01 за 1K токенов  
- **GPT-3.5 Turbo**: ~$0.002 за 1K токенов

### Anthropic Claude
- **Claude 3 Opus**: ~$0.015 за 1K токенов
- **Claude 3 Sonnet**: ~$0.003 за 1K токенов
- **Claude 3 Haiku**: ~$0.00025 за 1K токенов

### Бесплатные варианты
- **Ollama**: Полностью бесплатно (локальные модели)
- **Embeddings**: Всегда бесплатно (локальная обработка)

## 🔧 Оптимизация производительности

### Для быстрой работы
```env
LLM_PROVIDER=openai
OPENAI_MODEL=gpt-3.5-turbo
EMBEDDING_MODEL=all-MiniLM-L6-v2
MAX_CONCURRENT_REQUESTS=10
```

### Для лучшего качества
```env
LLM_PROVIDER=openai
OPENAI_MODEL=gpt-4
EMBEDDING_MODEL=all-mpnet-base-v2
MAX_CONCURRENT_REQUESTS=3
```

### Для экономии
```env
LLM_PROVIDER=anthropic
ANTHROPIC_MODEL=claude-3-haiku-20240307
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

## 🐛 Устранение проблем

### Ошибка загрузки embedding модели
```bash
# Очистить кэш
rm -rf ~/.cache/huggingface/

# Переустановить sentence-transformers
pip uninstall sentence-transformers
pip install sentence-transformers==4.1.0
```

### Ошибки LLM API
1. Проверьте API ключ
2. Проверьте лимиты аккаунта
3. Попробуйте другую модель
4. Используйте `LLM_PROVIDER=none` как fallback

### Медленная работа
1. Уменьшите `MAX_CLUSTERS`
2. Используйте более быструю embedding модель
3. Увеличьте `MAX_CONCURRENT_REQUESTS`
4. Используйте более быструю LLM модель

## 📊 Мониторинг качества

Система автоматически логирует:
- **Silhouette score** - качество кластеризации (чем выше, тем лучше)
- **Время обработки** - производительность
- **Количество кластеров** - результат автоматического определения

Пример логов:
```
🎯 Оптимальное количество кластеров: 3 (score: 0.456)
✅ Кластеризация завершена: 3 кластеров
✅ LLM сгенерировал названия: {0: "AI и ML", 1: "Новости техно", 2: "Вакансии"}
``` 