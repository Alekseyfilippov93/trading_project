from django.db import models


class Signal(models.Model):
    """
    Модель для хранения торговых сигналов и рассчитанных индикаторов.
    """
    cmf = models.FloatField(null=True, blank=True)
    BUY = "buy"
    SELL = "sell"

    SIGNAL_TYPES = [
        (BUY, "Buy"),
        (SELL, "Sell"),
    ]

    symbol = models.CharField(max_length=20)  # выбираем тикет акции, фьючерса, криптовалюты
    timeframe = models.CharField(max_length=10)  # 1m, 5m, 1h, за какой период хотим смотреть
    signal_type = models.CharField(max_length=10)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    # индикаторы
    rsi = models.FloatField(null=True, blank=True)
    macd = models.FloatField(null=True, blank=True)
    sma_200 = models.FloatField(null=True, blank=True)

    analysis = models.CharField(max_length=10, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=50, default="tradingview")

    def __str__(self):
        return f"{self.symbol} - {self.signal_type}"
