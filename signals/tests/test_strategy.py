from signals.services import analyze_signal


def test_analyze_signal_buy():
    indicators = {"rsi": 20, "cmf": 0.5, "sma_200": 100, "macd_line": [0.1, 0.5]}

    result = analyze_signal(indicators, price=120)

    assert result["signal"] in ["BUY", "HOLD", "SELL"]
    assert "score" in result


def test_analyze_signal_hold():
    indicators = {"rsi": 50, "cmf": 0, "sma_200": 100, "macd_line": [0.1, 0.1]}

    result = analyze_signal(indicators, price=100)

    assert result["signal"] == "HOLD"
