import numpy as np
from .moex_data import build_moex_dataset


# SMA


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


# RSI


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


# EMA


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


# MACD


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


# CMF


def calculate_cmf(
    highs: list[float],
    lows: list[float],
    closes: list[float],
    volumes: list[float],
    period: int = 20,
) -> float:
    """
    Chaikin Money Flow (устойчивый вариант)

    > 0 → BUY давление
    < 0 → SELL давление

    Всегда возвращает число (не None)
    """

    # 🔥 защита от мусора
    if not highs or not lows or not closes or not volumes:
        return 0.0

    length = min(len(highs), len(lows), len(closes), len(volumes))

    if length < period:
        period = length  # 🔥 адаптация под малые данные

    mfv = []
    vol_sum = 0

    for i in range(length - period, length):

        high = highs[i]
        low = lows[i]
        close = closes[i]
        volume = volumes[i]

        # защита от деления на 0
        if high == low:
            continue

        # защита от нулевых объёмов
        if volume <= 0:
            continue

        mfm = ((close - low) - (high - close)) / (high - low)
        mfv.append(mfm * volume)
        vol_sum += volume

    # 🔥 если всё отфильтровалось
    if vol_sum == 0 or not mfv:
        return 0.0

    cmf = sum(mfv) / vol_sum

    return float(cmf)


# INDICATORS


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


def calculate_score(indicators: dict, price: float) -> int:
    """Преобразует индикаторы в единый score (0–100)"""

    score = 50  # база (нейтральный рынок)

    rsi = indicators.get("rsi")
    cmf = indicators.get("cmf", 0)
    sma = indicators.get("sma_200")
    macd_line = indicators.get("macd_line")

    # RSI (перекупленность)

    if rsi is not None:
        if rsi < 30:
            score += 15
        elif rsi < 45:
            score += 5
        elif rsi > 70:
            score -= 15
        elif rsi > 55:
            score -= 5

    # TREND (SMA)

    if sma is not None:
        if price > sma:
            score += 10
        else:
            score -= 10

    # CMF (money flow)

    score += cmf * 20  # усиливаем влияние

    # MACD (momentum)

    if macd_line is not None and len(macd_line) > 1:
        if macd_line[-1] > macd_line[-2]:
            score += 10
        else:
            score -= 10

    # ограничение
    return max(0, min(100, int(score)))


# STRATEGY


def analyze_signal(indicators: dict, price: float) -> dict:
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
    score = calculate_score(indicators, price)
    reasons = explain_signal(indicators, price)

    if score >= 75:
        signal = "BUY"
    elif score <= 25:
        signal = "SELL"
    else:
        signal = "HOLD"

    return {"signal": signal, "score": score, "reasons": reasons}


# SIGNAL EXPLAIN


def explain_signal(indicators: dict, price: float) -> list[str]:
    """Возвращает причины сигнала"""

    reasons = []

    rsi = indicators.get("rsi")
    cmf = indicators.get("cmf", 0)
    sma = indicators.get("sma_200")

    if rsi is not None:
        if rsi < 30:
            reasons.append("RSI перепродан → бычий тренд")
        elif rsi > 70:
            reasons.append("RSI перекуплен → медвежий")

    if sma is not None:
        if price > sma:
            reasons.append("Цена выше скользящей средней → восходящий тренд")
        else:
            reasons.append("Цена ниже скользящей средней → нисходящий тренд")

    if cmf > 0:
        reasons.append("Положительный эффект CMF → давление покупателей")
    else:
        reasons.append("CMF отрицательный → давление со стороны продавцов")

    return reasons


def analyze_moex(symbol: str):
    data = build_moex_dataset(symbol)

    if not data or not data.get("closes"):
        return {"symbol": symbol, "error": "NO DATA"}

    indicators = calculate_indicators(data)
    signal = analyze_signal(indicators, data["price"])

    return {
        "symbol": symbol,
        "price": data["price"],
        "rsi": indicators["rsi"],
        "macd": indicators["macd"],
        "cmf": indicators["cmf"],
        "analysis": signal,
    }
