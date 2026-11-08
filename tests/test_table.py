import pandas as pd
import pytest

from conftest import snapshot
from model import WeatherData
from table import COLUMNS, format_table, measurements_table


@pytest.fixture
def data() -> WeatherData:
    d = WeatherData()
    d.add_measurement("Warszawa", "2024-10-07 12:00", 18.5)
    d.add_measurement("Kraków", "2024-10-07 12:00", 16.5)
    d.add_measurement("Łódź", "2024-10-06 12:00", 18.5)
    d.add_measurement("Kraków", "2024-10-08 12:00", 18.5)
    d.add_measurement("Gdańsk", "2024-10-09 12:00", 10.0)
    return d


def rows(frame: pd.DataFrame) -> list[tuple]:
    return [
        (loc, ts.strftime("%Y-%m-%d %H:%M"), val)
        for loc, ts, val in frame.itertuples(index=False)
    ]


def test_columns(data):
    frame = measurements_table(data)
    assert list(frame.columns) == COLUMNS
    assert len(frame) == 5


def test_sort_by_time_ascending_with_ties_by_location(data):
    result = rows(measurements_table(data, "czas", ascending=True))
    assert result == [
        ("Łódź", "2024-10-06 12:00", 18.5),
        ("Kraków", "2024-10-07 12:00", 16.5),   # remis czasu: Kraków < Warszawa
        ("Warszawa", "2024-10-07 12:00", 18.5),
        ("Kraków", "2024-10-08 12:00", 18.5),
        ("Gdańsk", "2024-10-09 12:00", 10.0),
    ]


def test_sort_by_time_descending(data):
    result = rows(measurements_table(data, "czas", ascending=False))
    assert [r[1] for r in result] == [
        "2024-10-09 12:00", "2024-10-08 12:00", "2024-10-07 12:00",
        "2024-10-07 12:00", "2024-10-06 12:00",
    ]
    assert [r[0] for r in result[2:4]] == ["Kraków", "Warszawa"]


def test_sort_by_temperature_ascending_ties_location_then_time(data):
    result = rows(measurements_table(data, "temperatura", ascending=True))
    assert result == [
        ("Gdańsk", "2024-10-09 12:00", 10.0),
        ("Kraków", "2024-10-07 12:00", 16.5),
        ("Kraków", "2024-10-08 12:00", 18.5),   # remis 18.5: Kraków, Łódź, Warszawa
        ("Łódź", "2024-10-06 12:00", 18.5),
        ("Warszawa", "2024-10-07 12:00", 18.5),
    ]


def test_sort_by_temperature_descending(data):
    result = rows(measurements_table(data, "temperatura", ascending=False))
    assert [r[0] for r in result] == ["Kraków", "Łódź", "Warszawa", "Kraków", "Gdańsk"]
    assert [r[2] for r in result] == [18.5, 18.5, 18.5, 16.5, 10.0]


def test_tie_same_location_same_temperature_sorted_by_time():
    d = WeatherData()
    d.add_measurement("A", "2024-10-09 12:00", 5.0)
    d.add_measurement("A", "2024-10-07 12:00", 5.0)
    d.add_measurement("A", "2024-10-08 12:00", 5.0)
    result = rows(measurements_table(d, "temperatura", ascending=False))
    assert [r[1][:10] for r in result] == ["2024-10-07", "2024-10-08", "2024-10-09"]


def test_sorting_does_not_change_measurements(data):
    before = snapshot(data)
    original_list = data.measurements
    measurements_table(data, "temperatura", ascending=False)
    measurements_table(data, "czas", ascending=True)
    assert data.measurements is original_list
    assert snapshot(data) == before


def test_empty_set():
    frame = measurements_table(WeatherData(), "czas")
    assert frame.empty
    assert list(frame.columns) == COLUMNS
    assert format_table(frame) == "Brak pomiarów do wyświetlenia."


def test_unknown_sort_key_raises(data):
    with pytest.raises(ValueError):
        measurements_table(data, "wilgotność")


def test_format_table_contains_values(data):
    text = format_table(measurements_table(data, "czas"))
    assert "Łódź" in text and "18.50 °C" in text and "2024-10-06 12:00" in text
