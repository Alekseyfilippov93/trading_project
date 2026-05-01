import requests


def build_moex_dataset(symbol: str):
    """
    Реальные свечи MOEX (history)
    """

    url = (
        "https://iss.moex.com/iss/history/engines/stock/"
        f"markets/shares/securities/{symbol}.json"
    )

    try:
        r = requests.get(url, timeout=10).json()

        history = r.get("history", {})
        data = history.get("data", [])
        cols = history.get("columns", [])

        if not data or not cols:
            return None

        closes = []
        highs = []
        lows = []
        volumes = []

        for row in data[-200:]:  # последние 200 свечей
            item = dict(zip(cols, row))

            close = item.get("CLOSE")
            high = item.get("HIGH")
            low = item.get("LOW")
            volume = item.get("VOLUME")

            if close is None:
                continue

            closes.append(float(close))
            highs.append(float(high) if high else float(close))
            lows.append(float(low) if low else float(close))
            volumes.append(float(volume) if volume else 0)

        if not closes:
            return None

        return {
            "symbol": symbol,
            "price": closes[-1],
            "closes": closes,
            "highs": highs,
            "lows": lows,
            "volumes": volumes,
        }

    except Exception as e:
        print("MOEX ERROR:", e)
        return None
