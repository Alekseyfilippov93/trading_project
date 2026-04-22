from django.db import models


class Signal(models.Model):
    """
    Модель для хранения торговых сигналов и рассчитанных индикаторов.

    Хранит:
    1. Базовую информацию об инструменте
    2. Рассчитанные технические индикаторы
    3. Результат записывается в формате JSOM

    Используется:
    1. Для хранения истории сигналов
    2. Отображение в dashbord
    """

    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"

    SIGNAL_TYPES = [
        (BUY, "Buy"),
        (SELL, "Sell"),
        (HOLD, "Hold"),
    ]

    symbol = models.CharField(
        max_length=20
    )  # выбираем тикет акции, фьючерса, криптовалюты
    timeframe = models.CharField(
        max_length=10, default="1h"
    )  # 1m, 5m, 1h, за какой период хотим смотреть
    signal_type = models.CharField(max_length=10, choices=SIGNAL_TYPES, default=HOLD)
    price = models.DecimalField(max_digits=12, decimal_places=2)

    # индикаторы
    rsi = models.FloatField(null=True, blank=True)
    macd = models.FloatField(null=True, blank=True)
    sma_200 = models.FloatField(null=True, blank=True)
    cmf = models.FloatField(null=True, blank=True)

    analysis = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    source = models.CharField(
        max_length=50,
        default="tradingview",
        help_text="Источник сигнала (TradingView, MOEX, manual)",
    )

    def __str__(self):
        return f"{self.symbol} - {self.signal_type}"
