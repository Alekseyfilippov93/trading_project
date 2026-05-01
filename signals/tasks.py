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

        # нормализуем сигнал
        signal_type = analysis.get("signal") if isinstance(analysis, dict) else analysis
        signal_type = str(signal_type or "hold").lower()[:10]

        Signal.objects.create(
            symbol=symbol,
            timeframe="1h",
            signal_type=signal_type,
            price=price,
            rsi=indicators.get("rsi"),
            macd=indicators.get("macd"),
            sma_200=indicators.get("sma_200"),
            cmf=indicators.get("cmf"),
            analysis=analysis,
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

        signal_type = str(result.get("signal") or "hold").lower()[:10]

        Signal.objects.create(
            symbol=symbol,
            timeframe="1d",
            signal_type=signal_type,
            price=result.get("price", 0),
            rsi=result.get("rsi"),
            macd=result.get("macd"),
            sma_200=result.get("sma_200"),
            cmf=result.get("cmf"),
            analysis=result,
            source="celery_moex",
        )

        log_signal(symbol, result.get("price", 0), signal_type)

        print(f"[MOEX] {symbol} updated → {signal_type}")
