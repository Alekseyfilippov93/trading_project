FROM python:3.11

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# системные зависимости (ВАЖНО для pandas/numpy)
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip setuptools wheel

COPY . /app

RUN pip install numpy pandas
RUN pip install --upgrade pip
RUN pip install django djangorestframework psycopg2-binary python-dotenv


CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]