# Trading Signals Dashboard

Проект: торговый терминал с автоматическим анализом рынка, расчетом индикаторов и веб-дашбордом.

---

## 🚀 Описание проекта

Веб-приложение для трейдеров, которое:

- принимает сигналы из TradingView (webhook)
- получает рыночные данные (Crypto + MOEX)
- рассчитывает технические индикаторы
- анализирует рынок и формирует сигналы
- сохраняет данные в БД
- отображает всё в веб-дашборде

---

## ⚙️ Основной функционал

### 1. Прием сигналов

- HTTP webhook от TradingView
- автоматическая обработка

### 2. Получение данных

- Crypto: Bybit API
- MOEX: ISS API Московской биржи

### 3. Аналитика

Рассчитываются индикаторы:

- SMA 200
- EMA
- RSI
- MACD
- Chaikin Money Flow (CMF)

---

### 4. Генерация сигналов

Система анализирует:

- тренд (SMA)
- импульс (MACD)
- перекупленность (RSI)
- поток денег (CMF)

И выдает:

- `BUY`
- `SELL`
- `HOLD`

---

### 5. Хранение данных

- PostgreSQL
- сохраняются:
    - цена
    - индикаторы
    - сигнал
    - время

---

### 6. Веб-дашборд

- LIVE блок (текущая цена + индикаторы)
- таблица сигналов
- фильтр по тикеру
- поддержка:
    - Crypto (BTCUSDT и др.)
    - MOEX (SBER, GAZP, LKOH, VTBR)

---

## Архитектура

TradingView → Django API → Анализ → PostgreSQL→Dashboard (HTML + JS)

---

## Технологии

### Backend

- Django
- Django REST Framework

### Data

- NumPy
- Pandas (частично)

### База данных

- PostgreSQL

### API

- Bybit API
- MOEX ISS API

### DevOps

- Docker
- Docker Compose

---

## Запуск проекта (Docker)

### 1. Клонирование

```bash
git clone <repo>
cd project
```

### 2. Запуск

```
docker-compose up --build
```

### 3. Применение миграций

```docker exec -it django_app python manage.py migrate```

### 4. Создание суперпользователя

```docker exec -it django_app python manage.py createsuperuser```

### 5. Открыть проект

Dashboard:

```
http://localhost:8000/
```

API:

```
http://localhost:8000/signals/
http://localhost:8000/analyze/?symbol=BTCUSDT
http://localhost:8000/analyze/?symbol=SBER
```

### 6. Автообновление данных

- каждые 4 секунды обновляется:

``` 
    цена
    индикаторы
    сигнал
    Поддержка MOEX
```

### 7. Поддерживаются тикеры:

~~~
SBER
GAZP
LKOH
VTBR
~~~

---

#### Если рынок закрыт:

используется последняя цена (cache)
данные не пропадают

---

### 📦 Структура проекта

signals/
├── services.py # индикаторы и стратегия
├── views.py # API endpoints
├── market.py # crypto данные
├── moex_data.py # MOEX API
├── models.py # БД
├── serializers.py
├── templates/signals
│ └── dashboard.html

---

### Будущие доработки

- 📩 Telegram уведомления
- 💰 платные подписки
- 📉 уровни Фибоначчи
- 📊 графики (TradingView / Chart.js)

---

## Вывод

### Система позволяет:

- автоматически анализировать рынок
- получать сигналы в реальном времени
- отслеживать историю
- работать с крипто и фондовым рынком

---

## Автор

Филиппов Алексей Сергеевич
