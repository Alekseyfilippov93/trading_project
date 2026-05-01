from django.urls import path
from .views import tradingview_webhook, dashboard, signals_list, analyze_market


urlpatterns = [
    path("webhook/", tradingview_webhook, name="tradingview-webhook"),
    path("dashboard/", dashboard),
    path("signals/", signals_list, name="signals-list"),
    path("analyze/", analyze_market),
]
