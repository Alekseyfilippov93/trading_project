from celery import shared_task
from .services import analyze_moex, calculate_indicators, analyze_signal
from .logger import log_signal
from .market import get_bybit_ohlcv
from .models import Signal


@shared_task
def update_crypto_signals():
    """
    Обновляет торговые сигналы для криптовалют.

    - получает OHLCV данные с биржи Bybit
    - считает индикаторы
    - генерирует торговый сигнал
    - сохраняет результат в БД
    """

    symbols = ["BTCUSDT", "ETHUSDT"]

    for symbol in symbols:
        data = get_bybit_ohlcv(symbol)

        if not data:
            continue

        price = data["closes"][-1]
        indicators = calculate_indicators(data)
        analysis = analyze_signal(indicators, price)

        Signal.objects.create(
            symbol=symbol,
            timeframe="1h",
            signal_type=analysis,
            price=price,
            rsi=indicators.get("rsi"),
            macd=indicators.get("macd"),
            sma_200=indicators.get("sma_200"),
            cmf=indicators.get("cmf"),
            analysis=str(analysis),
            source="celery_crypto",
        )

        log_signal(symbol, price, str(analysis))

        print(f"[CRYPTO] {symbol} updated → {analysis}")


@shared_task
def update_moex_signals():
    """
    Обновляет торговые сигналы для MOEX.

    - анализирует российский рынок
    - сохраняет результат в БД
    """

    symbols = ["SBER", "GAZP", "LKOH", "VTBR"]

    for symbol in symbols:
        result = analyze_moex(symbol)

        if not result:
            continue

        Signal.objects.create(
            symbol=symbol,
            timeframe="1d",
            signal_type=result.get("signal", "HOLD"),
            price=result.get("price", 0),
            rsi=result.get("rsi"),
            macd=result.get("macd"),
            sma_200=result.get("sma_200"),
            cmf=result.get("cmf"),
            analysis=str(result),
            source="celery_moex",
        )

        log_signal(symbol, result.get("price", 0), str(result.get("signal")))

        print(f"[MOEX] {symbol} updated → {result.get('signal')}")
