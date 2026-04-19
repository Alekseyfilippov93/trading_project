import numpy as np


# =========================
# SMA
# =========================
def calculate_sma(prices: list[float], period: int = 200) -> float | None:
    """
    Простая скользящая средняя (SMA).

    Args:
        prices: список цен закрытия
        period: период расчёта

    Returns:
        SMA или None если данных недостаточно
    """
    if len(prices) < period:
        return None

    return float(np.mean(prices[-period:]))


# =========================
# RSI
# =========================
def calculate_rsi(prices: list[float], period: int = 14) -> float | None:
    """
    Индекс относительной силы (RSI).

    Показывает перекупленность / перепроданность рынка.

    Args:
        prices: список цен закрытия
        period: период RSI

    Returns:
        RSI (0–100) или None
    """
    if len(prices) < period + 1:
        return None

    deltas = np.diff(prices)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)

    avg_gain = np.mean(gains[-period:])
    avg_loss = np.mean(losses[-period:])

    if avg_loss == 0:
        return 100.0

    rs = avg_gain / avg_loss
    return float(100 - (100 / (1 + rs)))


# =========================
# EMA
# =========================
def calculate_ema(prices: list[float], period: int) -> list[float]:
    """
    Экспоненциальная скользящая средняя (EMA).

    Args:
        prices: цены
        period: период

    Returns:
        список EMA значений
    """
    ema = []
    k = 2 / (period + 1)

    for i, price in enumerate(prices):
        if i == 0:
            ema.append(price)
        else:
            ema.append(price * k + ema[i - 1] * (1 - k))

    return ema


# =========================
# MACD
# =========================
def calculate_macd(prices: list[float]) -> list[float] | None:
    """
    MACD индикатор.

    Показывает импульс тренда.

    Returns:
        MACD линия или None
    """
    if len(prices) < 26:
        return None

    ema_12 = calculate_ema(prices, 12)
    ema_26 = calculate_ema(prices, 26)

    return (np.array(ema_12) - np.array(ema_26)).tolist()


def detect_macd_crossover(macd: list[float]) -> str | None:
    """
    Определяет пересечение MACD линии.

    Returns:
        BUY / SELL / None
    """
    if not macd or len(macd) < 2:
        return None

    if macd[-2] < 0 and macd[-1] > 0:
        return "BUY"

    if macd[-2] > 0 and macd[-1] < 0:
        return "SELL"

    return None


# =========================
# CMF
# =========================
def calculate_cmf(highs, lows, closes, volumes, period: int = 20) -> float | None:
    """
    Chaikin Money Flow (CMF).

    Показывает поток денег (покупатели/продавцы).

    > 0 = покупатели доминируют
    < 0 = продавцы доминируют

    Returns:
        CMF значение или None
    """
    if len(closes) < period:
        return None

    mfv_sum = 0
    vol_sum = 0

    for i in range(-period, 0):

        if highs[i] - lows[i] == 0:
            continue

        mfm = ((closes[i] - lows[i]) - (highs[i] - closes[i])) / (highs[i] - lows[i])
        mfv = mfm * volumes[i]

        mfv_sum += mfv
        vol_sum += volumes[i]

    if vol_sum == 0:
        return None

    return float(mfv_sum / vol_sum)


# =========================
# INDICATORS
# =========================
def calculate_indicators(data: dict) -> dict:
    """
    Рассчитывает все индикаторы.

    Args:
        data: OHLCV данные

    Returns:
        dict с индикаторами
    """

    closes = data["closes"]
    highs = data["highs"]
    lows = data["lows"]
    volumes = data["volumes"]

    macd_line = calculate_macd(closes)

    return {
        "rsi": calculate_rsi(closes),
        "macd": macd_line[-1] if macd_line else None,
        "macd_line": macd_line,
        "sma_200": calculate_sma(closes, 200),
        "cmf": calculate_cmf(highs, lows, closes, volumes),
    }


# =========================
# STRATEGY
# =========================
def analyze_signal(indicators: dict, price: float) -> str:
    """
    Торговая стратегия.

    Использует:
    - RSI
    - MACD
    - SMA тренд
    - CMF (поток денег)

    Returns:
        BUY / SELL / STRONG_BUY / STRONG_SELL / HOLD
    """

    rsi = indicators.get("rsi")
    macd_line = indicators.get("macd_line")
    sma_200 = indicators.get("sma_200")
    cmf = indicators.get("cmf")

    if None in (rsi, macd_line, sma_200):
        return "HOLD"

    crossover = detect_macd_crossover(macd_line)
    trend = "UP" if price > sma_200 else "DOWN"

    score = 0

    if trend == "UP":
        score += 1
    else:
        score -= 1

    if rsi < 35:
        score += 1
    elif rsi > 65:
        score -= 1

    if crossover == "BUY":
        score += 1
    elif crossover == "SELL":
        score -= 1

    if cmf is not None:
        if cmf > 0:
            score += 1
        else:
            score -= 1

    if score >= 3:
        return "STRONG_BUY"

    if score <= -3:
        return "STRONG_SELL"

    if score > 0:
        return "BUY"

    if score < 0:
        return "SELL"

    return "HOLD"