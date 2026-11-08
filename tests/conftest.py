import pytest

from model import WeatherData


@pytest.fixture
def data() -> WeatherData:
    return WeatherData()


def snapshot(data: WeatherData) -> list[tuple]:
    """Zwraca porównywalny obraz stanu zbioru pomiarów."""
    return [(m.location, m.measured_at, m.value) for m in data.measurements]
