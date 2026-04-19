import pytest
from signals.services import calculate_rsi, calculate_sma, calculate_cmf


def test_rsi_basic():
    prices = [1, 2, 3, 4, 5, 6, 7, 8, 9]

    rsi = calculate_rsi(prices, period=5)

    assert rsi is not None
    assert 0 <= rsi <= 100


def test_sma_basic():
    prices = [10, 20, 30, 40, 50]

    sma = calculate_sma(prices, period=5)

    assert sma == 30.0


def test_cmf_returns_number():
    highs = [10, 11, 12, 13]
    lows = [9, 10, 11, 12]
    closes = [9.5, 10.5, 11.5, 12.5]
    volumes = [100, 200, 300, 400]

    cmf = calculate_cmf(highs, lows, closes, volumes)

    assert isinstance(cmf, float)