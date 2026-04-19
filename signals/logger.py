import logging

logger = logging.getLogger("trading")


def log_signal(symbol: str, price: float, analysis: str):
    """
    Логирует торговый сигнал.

    Args:
        symbol (str): тикер
        price (float): цена
        analysis (str): результат стратегии
    """
    logger.info(f"[SIGNAL] {symbol} | price={price} | decision={analysis}")
