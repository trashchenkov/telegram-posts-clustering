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
    
    # Устанавливаем зависимости если requirements.txt новее
    if [ requirements.txt -nt venv/pyvenv.cfg ] || [ ! -f "venv/installed" ]; then
        echo "📦 Установка зависимостей..."
        pip install -r requirements.txt
        touch venv/installed
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
    
    # Устанавливаем зависимости если package.json новее
    if [ package.json -nt node_modules/.installed ] || [ ! -f "node_modules/.installed" ]; then
        echo "📦 Установка зависимостей..."
        npm install
        touch node_modules/.installed
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