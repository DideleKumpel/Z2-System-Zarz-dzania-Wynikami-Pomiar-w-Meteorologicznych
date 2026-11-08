"""Interfejs konsolowy systemu zarządzania wynikami pomiarów meteorologicznych."""

from __future__ import annotations

from analysis import TemperatureMatrix
from model import WeatherData
from table import format_table, measurements_table

MENU = """
1. Dodaj nowy pomiar
2. Wyświetl pomiary dla lokalizacji
3. Oblicz średnią temperaturę dla lokalizacji
4. Zapisz pomiary do pliku
5. Wczytaj pomiary z pliku
6. Wyświetl średnie temperatury dla kolejnych dni
7. Wyświetl maksimum w macierzy średnich dziennych
8. Wyjdź
9. Wyświetl tabelę pomiarów z sortowaniem (pandas)"""


def add_measurement(data: WeatherData) -> None:
    """Pobiera dane od użytkownika i dodaje pomiar."""
    location = input("Podaj lokalizację: ")
    measured_at = input("Podaj datę i godzinę (RRRR-MM-DD HH:MM): ")
    value = input("Podaj temperaturę w °C: ").replace(",", ".")
    data.add_measurement(location, measured_at, value)
    print("Pomiar dodany!")


def show_location(data: WeatherData) -> None:
    """Wyświetla pomiary wybranej lokalizacji."""
    location = input("Podaj lokalizację: ")
    found = data.get_measurements_by_location(location)
    if not found:
        print(f"Brak pomiarów dla lokalizacji '{location.strip()}'.")
        return
    for measurement in found:
        print(measurement)


def show_average(data: WeatherData) -> None:
    """Wyświetla średnią temperaturę lokalizacji."""
    location = input("Podaj lokalizację: ")
    average = data.get_average_temperature(location)
    print(f"Średnia temperatura dla lokalizacji {location.strip()} wynosi: {average:.2f} °C")


def save(data: WeatherData) -> None:
    """Zapisuje pomiary do pliku."""
    filename = input("Podaj nazwę pliku: ").strip()
    data.save_to_file(filename)
    print(f"Pomiary zapisane do pliku {filename}")


def load(data: WeatherData) -> None:
    """Wczytuje pomiary z pliku."""
    filename = input("Podaj nazwę pliku: ").strip()
    data.load_from_file(filename)
    print(f"Wczytano {len(data.measurements)} pomiarów z pliku {filename}")


def show_daily_averages(data: WeatherData) -> None:
    """Wyświetla średnie temperatury dla kolejnych dni (macierz budowana od nowa)."""
    matrix = TemperatureMatrix.from_weather_data(data)
    for day, average in zip(matrix.dates, matrix.get_average_per_day()):
        print(f"{day.isoformat()}: {average:.2f} °C")


def show_max(data: WeatherData) -> None:
    """Wyświetla maksimum w macierzy średnich dziennych (macierz budowana od nowa)."""
    matrix = TemperatureMatrix.from_weather_data(data)
    print(f"Maksimum w macierzy średnich dziennych: {matrix.get_max_temperature():.2f} °C")


def show_table(data: WeatherData) -> None:
    """Wyświetla tabelę pomiarów, opcjonalnie posortowaną po czasie lub temperaturze."""
    print("Sortowanie: 0 - bez sortowania, 1 - po czasie, 2 - po temperaturze")
    choice = input("Wybierz sortowanie: ").strip()
    keys = {"0": None, "1": "czas", "2": "temperatura"}
    if choice not in keys:
        raise ValueError("Nieznana opcja sortowania.")
    ascending = True
    if keys[choice] is not None:
        order = input("Kolejność (r - rosnąco, m - malejąco): ").strip().lower()
        if order not in ("r", "m"):
            raise ValueError("Nieznana kolejność sortowania.")
        ascending = order == "r"
    print(format_table(measurements_table(data, keys[choice], ascending)))


ACTIONS = {
    "1": add_measurement,
    "2": show_location,
    "3": show_average,
    "4": save,
    "5": load,
    "6": show_daily_averages,
    "7": show_max,
    "9": show_table,
}


def run() -> None:
    """Uruchamia menu w pętli aż do wybrania opcji 8."""
    data = WeatherData()
    print("Witaj w systemie zarządzania wynikami meteorologicznymi!")
    while True:
        print(MENU)
        try:
            choice = input("Wybierz opcję: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nDo widzenia!")
            return
        if choice == "8":
            print("Do widzenia!")
            return
        action = ACTIONS.get(choice)
        if action is None:
            print("Nieznana opcja, wybierz numer z menu.")
            continue
        try:
            action(data)
        except ValueError as error:
            print(f"Błąd danych: {error}")
        except OSError as error:
            print(f"Błąd pliku: {error}")
        except (EOFError, KeyboardInterrupt):
            print("\nPrzerwano operację.")
