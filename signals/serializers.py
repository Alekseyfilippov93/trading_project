from rest_framework import serializers
from .models import Signal


class SignalSerializer(serializers.ModelSerializer):
    """Serializer for Signal model.
    Используется для:
    - валидации входящих данных от TradingView
    - преобразования JSON → модель Signal
    - (в будущем) отдачи данных в API
    """

    class Meta:
        model = Signal
        fields = "__all__"