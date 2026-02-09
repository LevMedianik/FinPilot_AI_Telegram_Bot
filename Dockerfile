# Базовый имидж
FROM python:3.11-slim

# Системные зависимости (PyMuPDF, FAISS / numpy, SSL)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libgomp1 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Установка зависимостей Python
COPY requirements.txt ./
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir --prefer-binary -r requirements.txt

# Код проекта
COPY . .

# Запуск бота
CMD ["python", "bot.py"]
