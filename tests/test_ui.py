import subprocess
import sys
from pathlib import Path

import ui

ROOT = Path(__file__).resolve().parent.parent


def run_menu(monkeypatch, capsys, answers):
    feed = iter(answers)
    monkeypatch.setattr("builtins.input", lambda prompt="": next(feed))
    ui.run()
    return capsys.readouterr().out


def test_import_does_not_start_menu():
    code = "import main, ui, model, analysis, table; print('ok')"
    result = subprocess.run(
        [sys.executable, "-c", code], cwd=ROOT, input="", capture_output=True, text=True
    )
    assert result.returncode == 0
    assert result.stdout.strip() == "ok"


def test_example_session(monkeypatch, capsys, tmp_path):
    csv_path = str(tmp_path / "dane.csv")
    out = run_menu(monkeypatch, capsys, [
        "1", "Warszawa", "2024-10-07 12:00", "18.5",
        "1", "Warszawa", "2024-10-08 12:00", "20,0",
        "1", "Kraków", "2024-10-07 12:00", "16.5",
        "1", "Kraków", "2024-10-08 12:00", "18",
        "3", "Warszawa",
        "6", "7",
        "4", csv_path,
        "5", csv_path,
        "9", "2", "m",
        "8",
    ])
    assert "Pomiar dodany!" in out
    assert "19.25 °C" in out
    assert "2024-10-07: 17.50 °C" in out
    assert "2024-10-08: 19.00 °C" in out
    assert "Maksimum w macierzy średnich dziennych: 20.00 °C" in out
    assert "Wczytano 4 pomiarów" in out


def test_errors_do_not_stop_program(monkeypatch, capsys, tmp_path):
    out = run_menu(monkeypatch, capsys, [
        "x",                                   # nieznana opcja
        "1", "", "2024-10-07 12:00", "1",      # pusta lokalizacja
        "1", "A", "2024-10-07 12:00", "abc",   # zła temperatura
        "3", "A",                              # brak pomiarów
        "6",                                   # pusta macierz
        "5", str(tmp_path / "brak.csv"),       # brak pliku
        "2", "A",
        "8",
    ])
    assert "Nieznana opcja" in out
    assert out.count("Błąd danych") == 4
    assert "Błąd pliku" in out
    assert "Do widzenia!" in out
