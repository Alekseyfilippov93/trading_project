import numpy as np


def calculate_sma(prices: list[float], period: int = 200) -> float | None:
    """
    Рассчитывает функция простоя скользящая средняя (SMA).
    Аргументы:
        prices (list[float]): Список цен закрытия.
        period (int): Период для расчета SMA.

    Returns:
        float |  Значение SMA или None, если данных недостаточно.
    """
    if len(prices) < period:
        return None

    return float(np.mean(prices[-period:]))


def calculate_rsi(prices: list[float], period: int = 14) -> float | None:
    """
    Функция рассчитывает индекс относительной силы (RSI).

    Аргументы:
        prices (list[float]): Список цен закрытия.
        period (int): Период для расчета RSI.

    Returns:
        float | Значение RSI или None, если данных недостаточно.
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
    rsi = 100 - (100 / (1 + rs))

    return float(rsi)


def calculate_ema(prices: list[float], period: int) -> list[float]:
    """
    Экспоненциальную скользящую среднюю (EMA).

    Аргументы:
        prices (list[float]): список цен закрытия.
        period (int): EMA period.

    Returns:
        list[float]: EMA values.
    """
    ema = []
    k = 2 / (period + 1)

    for i, price in enumerate(prices):
        if i == 0:
            ema.append(price)
        else:
            ema.append(price * k + ema[i - 1] * (1 - k))

    return ema


def calculate_macd(prices: list[float]) -> list[float] | None:
    """
    MACD (индикатор сходимости и расхождения скользящих средних).

    Аргументы:
        prices (list[float]): список цен закрытия.

    Returns:
        float | None: MACD value or None if not enough data.
    """
    if len(prices) < 26:
        return None

    ema_12 = calculate_ema(prices, 12)  # периоды можно менять, настраивать под себя.
    ema_26 = calculate_ema(prices, 26)

    macd_line = np.array(ema_12) - np.array(ema_26)

    return macd_line.tolist()


def detect_macd_crossover(macd: list[float]) -> str | None:
    """
    Определяет пересечение MACD с нулевой линией.

    Args:
        macd (list[float]): MACD линия

    Returns:
        str | None: 'BUY', 'SELL' или None
    """
    if len(macd) < 2:
        return None

    prev = macd[-2]
    current = macd[-1]

    # ↑ пересечение вверх
    if prev < 0 and current > 0:
        return "BUY"

    # ↓ пересечение вниз
    if prev > 0 and current < 0:
        return "SELL"

    return None


def calculate_indicators(prices: list[float]) -> dict:
    macd_line = calculate_macd(prices)
    """
    Рассчитывает все технические индикаторы

    Аргументы:
        prices (list[float]): список цен закрытия.

    Returns:
        dict: словарь с рассчитанными индикаторами.
    """
    return {
        "rsi": calculate_rsi(prices),
        "macd": macd_line[-1] if macd_line is not None else None,
        "macd_line": macd_line,
        "sma_200": calculate_sma(prices, 200),
    }


def analyze_signal(indicators: dict, price: float) -> str:
    """
    Анализирует индикаторы и возвращает торговую рекомендацию.

    Стратегия:
        - Если цена выше SMA 200 → восходящий тренд → ищем BUY
        - Если цена ниже SMA 200 → нисходящий тренд → ищем SELL
        - RSI < 30 → перепроданность (BUY)
        - RSI > 70 → перекупленность (SELL)
        - MACD > 0 → бычий импульс
        - MACD < 0 → медвежий импульс

    Args:
        indicators (dict): Рассчитанные индикаторы (rsi, macd, sma_200)
        price (float): Текущая цена

    Returns:
        str: BUY / SELL / HOLD
    """

    rsi = indicators.get("rsi")
    macd = indicators.get("macd")
    sma_200 = indicators.get("sma_200")
    macd_line = indicators.get("macd_line")

    #  защита от None
    if rsi is None or macd is None or sma_200 is None or macd_line is None:
        return "HOLD"

    crossover = detect_macd_crossover(macd_line)

    #  определяем тренд
    trend = "UP" if price > sma_200 else "DOWN"

    #  логика стратегии
    if trend == "UP" and rsi < 30 and crossover == "BUY":
        return "STRONG_BUY"

    if trend == "DOWN" and rsi > 70 and crossover == "SELL":
        return "STRONG_SELL"

    if crossover == "BUY":
        return "BUY"

    if crossover == "SELL":
        return "SELL"

    return "HOLD"
