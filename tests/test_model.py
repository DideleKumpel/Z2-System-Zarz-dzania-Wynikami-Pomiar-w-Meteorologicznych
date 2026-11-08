import math
from datetime import datetime

import pytest

from conftest import snapshot
from model import Measurement, WeatherData


# --- Measurement -----------------------------------------------------------

def test_measurement_str():
    m = Measurement("  Warszawa ", datetime(2024, 10, 7, 12, 0), 18.5)
    assert m.location == "Warszawa"
    assert str(m) == "Warszawa, 2024-10-07 12:00, 18.5 °C"


def test_measurement_accepts_negative_temperature():
    m = Measurement("Suwałki", datetime(2024, 1, 1, 6, 0), -21.5)
    assert m.value == -21.5


# --- Dodanie i filtrowanie --------------------------------------------------

def test_add_and_filter_case_insensitive_chronological(data):
    data.add_measurement("Warszawa", "2024-10-07 18:00", 15.0)
    data.add_measurement("Kraków", "2024-10-07 12:00", 16.5)
    data.add_measurement("Warszawa", "2024-10-07 12:00", 18.5)

    found = data.get_measurements_by_location(" warszawa ")

    assert len(found) == 2
    assert all(m.location == "Warszawa" for m in found)
    assert [m.measured_at for m in found] == [
        datetime(2024, 10, 7, 12, 0),
        datetime(2024, 10, 7, 18, 0),
    ]


def test_filter_unknown_location_returns_empty_list(data):
    data.add_measurement("Warszawa", "2024-10-07 12:00", 18.5)
    assert data.get_measurements_by_location("Gdańsk") == []


# --- Walidacja --------------------------------------------------------------

@pytest.mark.parametrize(
    "location, measured_at, value",
    [
        ("", "2024-10-07 12:00", 10.0),             # pusta lokalizacja
        ("   ", "2024-10-07 12:00", 10.0),          # same spacje
        ("Warszawa", "2024-02-30 12:00", 10.0),     # niemożliwa data
        ("Warszawa", "2024-10-07 25:00", 10.0),     # niemożliwa godzina
        ("Warszawa", "07.10.2024 12:00", 10.0),     # zły format
        ("Warszawa", "2024-10-07", 10.0),           # brak godziny
        ("Warszawa", "2024-10-07 12:00", "abc"),    # nieliczbowa temperatura
        ("Warszawa", "2024-10-07 12:00", math.nan),
        ("Warszawa", "2024-10-07 12:00", "nan"),
        ("Warszawa", "2024-10-07 12:00", math.inf),
        ("Warszawa", "2024-10-07 12:00", -math.inf),
        ("Warszawa", "2024-10-07 12:00", "inf"),
        ("Warszawa", "2024-10-07 12:00", None),
    ],
)
def test_invalid_data_rejected_without_state_change(data, location, measured_at, value):
    data.add_measurement("Kraków", "2024-10-07 12:00", 16.5)
    before = snapshot(data)
    with pytest.raises(ValueError):
        data.add_measurement(location, measured_at, value)
    assert snapshot(data) == before


def test_duplicate_rejected_case_and_space_insensitive(data):
    data.add_measurement("Warszawa", "2024-10-07 12:00", 18.5)
    before = snapshot(data)
    with pytest.raises(ValueError):
        data.add_measurement("  WARSZAWA ", "2024-10-07 12:00", 20.0)
    assert snapshot(data) == before


def test_same_time_different_location_is_not_duplicate(data):
    data.add_measurement("Warszawa", "2024-10-07 12:00", 18.5)
    data.add_measurement("Kraków", "2024-10-07 12:00", 16.5)
    assert len(data.measurements) == 2


# --- Średnia dla lokalizacji ------------------------------------------------

def test_average_temperature(data):
    data.add_measurement("Warszawa", "2024-10-07 12:00", 10.0)
    data.add_measurement("warszawa", "2024-10-08 12:00", 14.0)
    data.add_measurement("Kraków", "2024-10-07 12:00", 100.0)
    assert data.get_average_temperature("Warszawa") == pytest.approx(12.0, abs=1e-6)


def test_average_unknown_location_raises(data):
    data.add_measurement("Warszawa", "2024-10-07 12:00", 10.0)
    with pytest.raises(ValueError):
        data.get_average_temperature("Gdańsk")


def test_average_empty_set_raises(data):
    with pytest.raises(ValueError):
        data.get_average_temperature("Warszawa")


def test_model_does_not_use_input_or_print(data, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("model nie może używać input()/print()")

    monkeypatch.setattr("builtins.input", forbidden)
    monkeypatch.setattr("builtins.print", forbidden)
    data.add_measurement("Warszawa", "2024-10-07 12:00", 10.0)
    data.get_measurements_by_location("Warszawa")
    data.get_average_temperature("Warszawa")
    with pytest.raises(ValueError):
        data.add_measurement("", "2024-10-07 12:00", 10.0)
