import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_analyze_crypto():
    client = APIClient()

    response = client.get("/analyze/?symbol=BTCUSDT")

    assert response.status_code in [200, 400]


@pytest.mark.django_db
def test_analyze_moex():
    client = APIClient()

    response = client.get("/analyze/?symbol=SBER")

    # может быть 200 или 400 если рынок закрыт
    assert response.status_code in [200, 400]


@pytest.mark.django_db
def test_signals_list():
    client = APIClient()

    response = client.get("/signals/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
