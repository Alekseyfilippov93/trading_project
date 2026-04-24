from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import render

from .models import Signal
from .serializers import SignalSerializer
from .services import calculate_indicators, analyze_signal, analyze_moex
from .market import get_bybit_ohlcv
from .logger import log_signal
from django_filters.rest_framework import DjangoFilterBackend


@api_view(["POST"])
def tradingview_webhook(request):
    """
    Получение сигналов от TradingView + анализ рынка + сохранение в БД
    """

    data = request.data

    symbol = data.get("symbol")

    # 🔥 1. Получаем OHLCV данные с Bybit
    market_data = get_bybit_ohlcv(symbol)

    if not market_data:
        return Response({"error": "No market data"}, status=400)

    # 🔥 2. Берём текущую цену
    price = market_data["closes"][-1]

    # 🔥 3. Считаем индикаторы (RSI, MACD, SMA, CMF и т.д.)
    indicators = calculate_indicators(market_data)

    # 🔥 4. Анализ сигнала
    analysis = analyze_signal(indicators, price)

    # 🔥 5. Логирование
    log_signal(symbol, price, analysis)

    # 🔥 6. Сохранение в БД (ВКЛЮЧАЯ CMF)
    signal = Signal.objects.create(
        symbol=symbol,
        timeframe=data.get("timeframe"),
        signal_type=data.get("signal_type"),
        price=price,
        rsi=indicators["rsi"],
        macd=indicators["macd"],
        sma_200=indicators["sma_200"],
        cmf=indicators["cmf"],
        analysis=analysis,
    )

    # 🔥 7. Ответ API
    return Response(
        {
            "id": signal.id,
            "symbol": symbol,
            "price": price,
            "rsi": indicators["rsi"],
            "macd": indicators["macd"],
            "sma_200": indicators["sma_200"],
            "cmf": indicators["cmf"],
            "analysis": analysis,
        },
        status=status.HTTP_201_CREATED,
    )


# -----------------------------------------------------


def dashboard(request):
    """UI dashboard"""
    signals = Signal.objects.order_by("-created_at")[:50]
    return render(request, "signals/dashboard.html", {"signals": signals})


# -----------------------------------------------------


@api_view(["GET"])
def signals_list(request):
    """
    AJAX список сигналов
    """

    symbol = request.GET.get("symbol")
    timeframe = request.GET.get("timeframe")
    signal_type = request.GET.get("signal_type")

    signals = Signal.objects.all().order_by("-created_at")

    if symbol:
        signals = signals.filter(symbol__icontains=symbol)

    if timeframe:
        signals = signals.filter(timeframe=timeframe)

    if signal_type:
        signals = signals.filter(signal_type=signal_type)

    serializer = SignalSerializer(signals[:50], many=True)

    return Response(serializer.data)


# -----------------------------------------------------


@api_view(["GET"])
def analyze_market(request):
    """Ручной анализ рынка без webhook"""

    symbol = request.GET.get("symbol", "BTCUSDT")

    #  MOEX РФ
    if symbol in ["SBER", "GAZP", "LKOH", "VTBR", "MOEX"]:
        result = analyze_moex(symbol)

        if not result:
            return Response({"error": "No MOEX data"}, status=400)

        return Response(result)

    # 🔥 CRYPTO рынок
    market_data = get_bybit_ohlcv(symbol)

    if not market_data:
        return Response({"error": "No market data"}, status=400)

    price = market_data["closes"][-1]

    indicators = calculate_indicators(market_data)
    analysis = analyze_signal(indicators, price)

    return Response(
        {
            "symbol": symbol,
            "price": price,
            "rsi": indicators["rsi"],
            "macd": indicators["macd"],
            "sma_200": indicators["sma_200"],
            "cmf": indicators["cmf"],
            "analysis": analysis,
        }
    )
