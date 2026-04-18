from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Signal
from .serializers import SignalSerializer
from .services import calculate_indicators, analyze_signal
from .market import get_bybit_prices
from .logger import log_signal
from django.shortcuts import render


@api_view(["POST"])
def tradingview_webhook(request):
    """Получение сигналов от TradingView, вычисляет показатели и сохраняет их в БД
    Ниже пример в формате Json
    {
        "symbol": "SBER",
        "signal_type": "buy",
        "price": 256.4,
        "timeframe": "5m"
    }

    Как происходит сбор сигнала
    1. Получает POST-запрос от TradingView
    2. Валидирует данные через serializer
    3. Сохраняет сигнал в базу данных
    4. Возвращает статус

    Вывод:
        201 CREATED – если успешно сохранено
        400 BAD REQUEST – если ошибка в данных
    """

    data = request.data

    symbol = data.get("symbol")

    # данные с байбит биржи
    prices = get_bybit_prices(symbol)

    if not prices:
        return Response({"error": "No market data"}, status=400)

    price = prices[-1]  # РЕАЛЬНАЯ текущая цена в данный момент

    indicators = calculate_indicators(prices)
    analysis = analyze_signal(indicators, price)
    log_signal(symbol, price, analysis)

    signal = Signal.objects.create(
        symbol=symbol,
        timeframe=data.get("timeframe"),
        signal_type=data.get("signal_type"),
        price=price,
        rsi=indicators["rsi"],
        macd=indicators["macd"],
        sma_200=indicators["sma_200"],
        analysis=analysis,
    )

    return Response(
        {
            "id": signal.id,
            "symbol": symbol,
            "price": price,
            "rsi": indicators["rsi"],
            "macd": indicators["macd"],
            "sma_200": indicators["sma_200"],
            "analysis": analysis,
        },
        status=status.HTTP_201_CREATED,
    )


def dashboard(request):
    """Отображает список последних сигналов."""
    signals = Signal.objects.order_by("-created_at")[:50]

    return render(request, "signals/dashboard.html", {"signals": signals})

@api_view(["GET"])
def signals_list(request):
    """
    Возвращает последние сигналы для AJAX dashboard
    """
    symbol = request.GET.get("symbol")

    signals = Signal.objects.order_by("-created_at")

    if symbol:
        signals = signals.filter(symbol=symbol)

    serializer = SignalSerializer(signals[:50], many=True)
    return Response(serializer.data)
