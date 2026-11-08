"""Analiza dzienna: macierz średnich temperatur (lokalizacje x dni) w NumPy."""

from __future__ import annotations

from collections import defaultdict
from datetime import date

import numpy as np

from model import WeatherData, location_sort_key, normalize_location


class TemperatureMatrix:
    """Macierz średnich dziennych temperatur: wiersze to lokalizacje, kolumny to dni."""

    def __init__(self, matrix: np.ndarray, locations: list[str], dates: list[date]) -> None:
        """Tworzy macierz z gotowych danych (zwykle używaj from_weather_data)."""
        self.matrix: np.ndarray = matrix
        self.locations: list[str] = locations
        self.dates: list[date] = dates

    @classmethod
    def from_weather_data(cls, data: WeatherData) -> "TemperatureMatrix":
        """Buduje nową macierz z aktualnych pomiarów WeatherData.

        Kilka pomiarów lokalizacji w jednym dniu jest uśredniane do jednej komórki.
        Pusty zbiór lub brak pary lokalizacja–dzień powoduje ValueError.
        """
        if not data.measurements:
            raise ValueError("Brak pomiarów: nie można zbudować macierzy.")

        names: dict[str, str] = {}
        cells: dict[tuple[str, date], list[float]] = defaultdict(list)
        for m in data.measurements:
            key = normalize_location(m.location)
            names.setdefault(key, m.location)
            cells[(key, m.measured_at.date())].append(m.value)

        location_keys = sorted(names, key=lambda k: location_sort_key(names[k]))
        dates = sorted({day for _, day in cells})

        missing = [
            f"{names[key]} {day.isoformat()}"
            for key in location_keys
            for day in dates
            if (key, day) not in cells
        ]
        if missing:
            raise ValueError("Brak danych dla par lokalizacja–dzień: " + ", ".join(missing))

        matrix = np.array(
            [[np.mean(cells[(key, day)]) for day in dates] for key in location_keys],
            dtype=float,
        )
        return cls(matrix, [names[k] for k in location_keys], dates)

    def get_average_per_day(self) -> np.ndarray:
        """Zwraca średnie po lokalizacjach dla kolejnych dni (każda lokalizacja ma równą wagę)."""
        return self.matrix.mean(axis=0)

    def get_max_temperature(self) -> float:
        """Zwraca maksimum z komórek macierzy (najwyższą średnią dzienną lokalizacji)."""
        return float(self.matrix.max())
