import numpy as np
import pytest

from analysis import TemperatureMatrix
from model import WeatherData


def example() -> WeatherData:
    data = WeatherData()
    data.add_measurement("Warszawa", "2024-10-07 12:00", 18.5)
    data.add_measurement("Warszawa", "2024-10-08 12:00", 20.0)
    data.add_measurement("Kraków", "2024-10-07 12:00", 16.5)
    data.add_measurement("Kraków", "2024-10-08 12:00", 18.0)
    return data


def test_example_matrix():
    m = TemperatureMatrix.from_weather_data(example())
    assert isinstance(m.matrix, np.ndarray) and m.matrix.ndim == 2
    assert m.locations == ["Kraków", "Warszawa"]
    assert [d.isoformat() for d in m.dates] == ["2024-10-07", "2024-10-08"]
    np.testing.assert_allclose(m.matrix, [[16.5, 18.0], [18.5, 20.0]], atol=1e-6)
    np.testing.assert_allclose(m.get_average_per_day(), [17.5, 19.0], atol=1e-6)
    assert m.get_max_temperature() == pytest.approx(20.0, abs=1e-6)


def test_days_sorted_chronologically_regardless_of_insertion():
    data = WeatherData()
    data.add_measurement("A", "2024-10-09 12:00", 3.0)
    data.add_measurement("A", "2024-10-07 12:00", 1.0)
    data.add_measurement("A", "2024-10-08 12:00", 2.0)
    m = TemperatureMatrix.from_weather_data(data)
    assert [d.day for d in m.dates] == [7, 8, 9]
    np.testing.assert_allclose(m.matrix, [[1.0, 2.0, 3.0]])


def test_polish_alphabetical_order():
    data = WeatherData()
    for name in ["Warszawa", "Łódź", "Kraków"]:
        data.add_measurement(name, "2024-10-07 12:00", 1.0)
    assert TemperatureMatrix.from_weather_data(data).locations == ["Kraków", "Łódź", "Warszawa"]


def test_daily_aggregation():
    data = WeatherData()
    data.add_measurement("Warszawa", "2024-10-07 08:00", 10.0)
    data.add_measurement("Warszawa", "2024-10-07 20:00", 14.0)
    m = TemperatureMatrix.from_weather_data(data)
    assert m.matrix.shape == (1, 1)
    assert m.matrix[0, 0] == pytest.approx(12.0, abs=1e-6)


def test_each_location_has_equal_weight_per_day():
    data = WeatherData()
    data.add_measurement("A", "2024-10-07 06:00", 10.0)
    data.add_measurement("A", "2024-10-07 12:00", 10.0)
    data.add_measurement("A", "2024-10-07 18:00", 10.0)
    data.add_measurement("B", "2024-10-07 12:00", 20.0)
    m = TemperatureMatrix.from_weather_data(data)
    np.testing.assert_allclose(m.get_average_per_day(), [15.0], atol=1e-6)


def test_max_is_max_of_daily_means_not_single_measurement():
    data = WeatherData()
    data.add_measurement("A", "2024-10-07 06:00", 0.0)
    data.add_measurement("A", "2024-10-07 12:00", 30.0)
    assert TemperatureMatrix.from_weather_data(data).get_max_temperature() == pytest.approx(15.0)


def test_missing_location_day_raises():
    data = example()
    data.add_measurement("Gdańsk", "2024-10-07 12:00", 12.0)  # brak 2024-10-08
    with pytest.raises(ValueError) as error:
        TemperatureMatrix.from_weather_data(data)
    assert "Gdańsk 2024-10-08" in str(error.value)


def test_empty_set_raises():
    with pytest.raises(ValueError):
        TemperatureMatrix.from_weather_data(WeatherData())


def test_matrix_reflects_current_data():
    data = example()
    first = TemperatureMatrix.from_weather_data(data)
    data.add_measurement("Kraków", "2024-10-08 18:00", 30.0)
    second = TemperatureMatrix.from_weather_data(data)
    assert first.matrix[0, 1] == pytest.approx(18.0)
    assert second.matrix[0, 1] == pytest.approx(24.0)
