# Базовый образ: Python 3.11 (стабильный, проверенный)
FROM python:3.11-slim

# Рабочая папка внутри контейнера
WORKDIR /app

# Копируем список зависимостей
COPY requirements.txt .

# Устанавливаем библиотеки
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код и модель
COPY app/ ./app/
COPY models/ ./models/

# Открываем порт (документация)
EXPOSE 8000

# Команда запуска
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]