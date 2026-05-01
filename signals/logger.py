import logging

logger = logging.getLogger("trading")


def log_signal(symbol: str, price: float, analysis: dict):
    """
    Логирует торговый сигнал.

    Args:
        symbol (str): тикер инструмента
        price (float): цена инструмента на данный момент
        analysis (dict): результат стратегии
    """
    signal = analysis.get("signal") if isinstance(analysis, dict) else analysis

    logger.info(f"[SIGNAL] {symbol} | price={price} | signal={signal}")
