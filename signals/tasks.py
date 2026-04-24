from celery import shared_task
from .services import analyze_moex, calculate_indicators, analyze_signal
from .market import get_bybit_ohlcv


@shared_task
def update_crypto_signals():
    symbols = ["BTCUSDT", "ETHUSDT"]

    for symbol in symbols:
        data = get_bybit_ohlcv(symbol)

        if not data:
            continue

        price = data["closes"][-1]
        indicators = calculate_indicators(data)
        analysis = analyze_signal(indicators, price)

        print(f"[CRYPTO] {symbol} updated")


@shared_task
def update_moex_signals():
    symbols = ["SBER", "GAZP", "LKOH", "VTBR"]

    for symbol in symbols:
        result = analyze_moex(symbol)

        if not result:
            continue

        print(f"[MOEX] {symbol} updated")