import requests


def get_bybit_prices(symbol: str = "BTCUSDT", limit: int = 100) -> list[float]:
    """
    Получает исторические цены (свечи\бары) с Bybit.
    Используется публичный REST API Bybit для получения OHLC данных.
    Мы берем цену закрытия (close) каждой свечи.

    Args:
        symbol (str): Торговая пара (например BTCUSDT)
        limit (int): Количество свечей (макс ~200)

    Returns:
        list[float]: Список цен закрытия (от старых к новым)
    """

    url = "https://api.bybit.com/v5/market/kline"

    params = {
        "category": "linear",   # USDT
        "symbol": symbol,
        "interval": "1",        # 1 минута. Здесь можно заменить на какой интервал хотел бы пользователь
        "limit": limit,
    }

    response = requests.get(url, params=params)

    # защита от кривого ответа
    if response.status_code != 200:
        raise Exception(f"Bybit API error: {response.status_code}")

    data = response.json()

    if "result" not in data:
        raise Exception("Invalid Bybit response")

    candles = data["result"]["list"]

    # [timestamp, open, high, low, close, volume]
    prices = [float(candle[4]) for candle in candles]

    # Bybit возвращает новые → старые, переворачиваем
    return prices[::-1]