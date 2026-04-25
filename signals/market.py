import requests


def get_bybit_ohlcv(
    symbol: str = "BTCUSDT", timeframe: str = "1h", limit: int = 300
) -> dict:
    """
    Получает OHLCV данные (свечи) с Bybit.

    Args:
        symbol (str): Торговая пара
        limit (int): Количество свечей

    Returns:
        dict:
            {
                "closes": [...],
                "highs": [...],
                "lows": [...],
                "volumes": [...]
            }
    """

    url = "https://api.bybit.com/v5/market/kline"

    # 🔥 маппинг таймфреймов
    interval_map = {
        "15m": "15",
        "1h": "60",
        "1d": "D",
    }

    interval = interval_map.get(timeframe, "60")

    params = {
        "category": "linear",
        "symbol": symbol,
        "interval": interval,
        "limit": limit,
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise Exception(f"Bybit API error: {response.status_code}")

    data = response.json()

    candles = data["result"]["list"]

    candles = candles[::-1]

    closes = []
    highs = []
    lows = []
    volumes = []

    for c in candles:
        closes.append(float(c[4]))
        highs.append(float(c[2]))
        lows.append(float(c[3]))
        volumes.append(float(c[5]))

    return {
        "closes": closes,
        "highs": highs,
        "lows": lows,
        "volumes": volumes,
    }
