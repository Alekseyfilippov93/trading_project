FROM python:3.11

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

#системные зависимости

RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# обновляем pip

RUN pip install --upgrade pip

#копируем проект

COPY . /app

#устанавливаем зависимости

RUN pip install --no-cache-dir -r requirements.txt
