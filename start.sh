#!/bin/bash

echo "🚀 Запуск Telegram Posts Aggregator"
echo "=================================="

# Проверяем наличие Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не найден. Установите Python 3.8+"
    exit 1
fi

# Проверяем наличие Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js не найден. Установите Node.js 16+"
    exit 1
fi

echo "✅ Python и Node.js найдены"

# Функция для проверки Python зависимостей
check_python_deps() {
    echo "🔍 Проверка Python зависимостей..."
    
    # Проверяем основные пакеты
    python -c "
import sys
missing = []
try:
    import fastapi
    import uvicorn
    import sentence_transformers
    import sklearn
    import openai
    import httpx
    import bs4
    print('✅ Основные зависимости найдены')
except ImportError as e:
    missing.append(str(e))
    print('❌ Некоторые зависимости отсутствуют')
    sys.exit(1)
" 2>/dev/null
    return $?
}

# Функция для проверки Node.js зависимостей  
check_node_deps() {
    echo "🔍 Проверка Node.js зависимостей..."
    
    if [ ! -d "node_modules" ]; then
        return 1
    fi
    
    # Проверяем основные пакеты
    if [ ! -d "node_modules/react" ] || [ ! -d "node_modules/vite" ] || [ ! -d "node_modules/typescript" ]; then
        return 1
    fi
    
    echo "✅ Node.js зависимости найдены"
    return 0
}

# Функция для запуска backend
start_backend() {
    echo "🐍 Запуск Backend..."
    cd backend
    
    # Создаем виртуальное окружение если не существует
    if [ ! -d "venv" ]; then
        echo "📦 Создание виртуального окружения..."
        python3 -m venv venv
    fi
    
    # Активируем виртуальное окружение
    source venv/bin/activate
    
    # Проверяем нужна ли установка зависимостей
    NEED_INSTALL=false
    
    # Если requirements.txt новее чем последняя установка
    if [ requirements.txt -nt venv/pyvenv.cfg ]; then
        NEED_INSTALL=true
        echo "📝 requirements.txt обновлен"
    fi
    
    # Если файл-маркер установки не существует
    if [ ! -f "venv/installed" ]; then
        NEED_INSTALL=true
        echo "📝 Маркер установки не найден"
    fi
    
    # Если основные зависимости отсутствуют
    if ! check_python_deps; then
        NEED_INSTALL=true
        echo "📝 Отсутствуют основные зависимости"
    fi
    
    # Устанавливаем только если нужно
    if [ "$NEED_INSTALL" = true ]; then
        echo "📦 Установка Python зависимостей..."
        pip install -r requirements.txt
        if [ $? -eq 0 ]; then
        touch venv/installed
            echo "✅ Зависимости установлены"
        else
            echo "❌ Ошибка установки зависимостей"
            exit 1
        fi
    else
        echo "✅ Python зависимости уже установлены"
    fi
    
    # Создаем .env если не существует
    if [ ! -f ".env" ]; then
        echo "⚙️ Создание конфигурации..."
        cp env.example .env
        echo "📝 Отредактируйте backend/.env для настройки LLM провайдера"
    fi
    
    echo "🚀 Запуск API сервера на http://localhost:8000"
    python main.py &
    BACKEND_PID=$!
    cd ..
}

# Функция для запуска frontend
start_frontend() {
    echo "⚛️ Запуск Frontend..."
    
    # Проверяем нужна ли установка зависимостей
    NEED_INSTALL=false
    
    # Если package.json новее чем node_modules
    if [ package.json -nt node_modules/.installed ] || [ ! -f "node_modules/.installed" ]; then
        NEED_INSTALL=true
        echo "📝 package.json обновлен или маркер не найден"
    fi
    
    # Если основные зависимости отсутствуют
    if ! check_node_deps; then
        NEED_INSTALL=true
        echo "📝 Отсутствуют основные зависимости"
    fi
    
    # Устанавливаем только если нужно
    if [ "$NEED_INSTALL" = true ]; then
        echo "📦 Установка Node.js зависимостей..."
        npm install
        if [ $? -eq 0 ]; then
        touch node_modules/.installed
            echo "✅ Зависимости установлены"
        else
            echo "❌ Ошибка установки зависимостей"
            exit 1
        fi
    else
        echo "✅ Node.js зависимости уже установлены"
    fi
    
    echo "🚀 Запуск UI на http://localhost:5173"
    npm run dev &
    FRONTEND_PID=$!
}

# Функция для остановки процессов
cleanup() {
    echo ""
    echo "🛑 Остановка сервисов..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
    fi
    exit 0
}

# Обработчик сигналов
trap cleanup SIGINT SIGTERM

# Запускаем сервисы
start_backend
sleep 3
start_frontend

echo ""
echo "✅ Сервисы запущены!"
echo "📖 Backend API: http://localhost:8000/docs"
echo "🌐 Frontend UI: http://localhost:5173"
echo ""
echo "Нажмите Ctrl+C для остановки"

# Ждем завершения
wait 