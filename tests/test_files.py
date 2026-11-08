from datetime import datetime

import pytest

from conftest import snapshot
from model import WeatherData

HEADER = "location,measured_at,value\n"


def write(path, text):
    path.write_text(text, encoding="utf-8")
    return str(path)


def test_save_format(tmp_path, data):
    data.add_measurement("Warszawa", "2024-10-07 12:00", 18.5)
    data.add_measurement("Kraków", "2024-10-07 12:00", 16.5)
    path = tmp_path / "out.csv"
    data.save_to_file(str(path))
    assert path.read_text(encoding="utf-8").splitlines() == [
        "location,measured_at,value",
        "Warszawa,2024-10-07 12:00,18.5",
        "Kraków,2024-10-07 12:00,16.5",
    ]


def test_save_overwrites_file(tmp_path, data):
    path = tmp_path / "out.csv"
    path.write_text("stara zawartość\n" * 10, encoding="utf-8")
    data.add_measurement("Warszawa", "2024-10-07 12:00", 18.5)
    data.save_to_file(str(path))
    assert "stara" not in path.read_text(encoding="utf-8")


def test_round_trip_keeps_polish_characters(tmp_path, data):
    data.add_measurement("Łódź", "2024-10-07 08:15", -3.25)
    data.add_measurement("Zielona Góra", "2024-10-07 12:00", 0.1)
    data.add_measurement("Gdańsk, port", "2024-12-31 23:59", 7.0)  # przecinek w nazwie
    path = str(tmp_path / "dane.csv")
    data.save_to_file(path)

    loaded = WeatherData()
    loaded.load_from_file(path)
    assert snapshot(loaded) == snapshot(data)
    assert loaded.measurements[0].measured_at == datetime(2024, 10, 7, 8, 15)


def test_load_replaces_previous_data(tmp_path, data):
    data.add_measurement("Stare", "2020-01-01 00:00", 1.0)
    path = write(tmp_path / "in.csv", HEADER + "Warszawa,2024-10-07 12:00,18.5\n")
    data.load_from_file(path)
    assert snapshot(data) == [("Warszawa", datetime(2024, 10, 7, 12, 0), 18.5)]


def test_header_only_gives_empty_set(tmp_path, data):
    data.add_measurement("Warszawa", "2024-10-07 12:00", 18.5)
    data.load_from_file(write(tmp_path / "empty.csv", HEADER))
    assert data.measurements == []


@pytest.mark.parametrize(
    "content, line",
    [
        ("", None),                                                    # pusty plik
        ("Warszawa,2024-10-07 12:00,18.5\n", None),                    # brak nagłówka
        ("lokalizacja,data,wartosc\nWarszawa,2024-10-07 12:00,18.5\n", None),  # zły nagłówek
        (HEADER + "Warszawa,2024-10-07 12:00\n", 2),                   # za mało pól
        (HEADER + "Warszawa,2024-10-07 12:00,1,2\n", 2),               # za dużo pól
        (HEADER + "Warszawa,2024-10-07 12:00,18.5\n,2024-10-08 12:00,1\n", 3),   # pusta lokalizacja
        (HEADER + "Warszawa,2024-13-07 12:00,18.5\n", 2),              # zła data
        (HEADER + "Warszawa,2024-10-07 12:00,abc\n", 2),               # zła wartość
        (HEADER + "Warszawa,2024-10-07 12:00,nan\n", 2),               # NaN
        (HEADER + "Warszawa,2024-10-07 12:00,18.5\nwarszawa ,2024-10-07 12:00,1\n", 3),  # duplikat
    ],
)
def test_invalid_file_does_not_change_state(tmp_path, data, content, line):
    data.add_measurement("Kraków", "2024-10-07 12:00", 16.5)
    before = snapshot(data)
    path = write(tmp_path / "bad.csv", content)
    with pytest.raises(ValueError) as error:
        data.load_from_file(path)
    assert snapshot(data) == before
    if line is not None:
        assert f"Wiersz {line}" in str(error.value)


def test_missing_file_raises_oserror(tmp_path, data):
    data.add_measurement("Kraków", "2024-10-07 12:00", 16.5)
    before = snapshot(data)
    with pytest.raises(FileNotFoundError):
        data.load_from_file(str(tmp_path / "nie_ma.csv"))
    assert snapshot(data) == before


def test_save_to_invalid_path_raises_oserror(tmp_path, data):
    with pytest.raises(OSError):
        data.save_to_file(str(tmp_path / "brak_katalogu" / "out.csv"))


def test_sample_csv_is_valid(data):
    from pathlib import Path

    sample = Path(__file__).resolve().parent.parent / "dane_pomiarowe.csv"
    data.load_from_file(str(sample))
    assert len(data.measurements) == 7
