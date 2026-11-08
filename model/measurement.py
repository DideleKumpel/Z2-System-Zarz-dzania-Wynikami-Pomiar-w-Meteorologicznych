"""Klasa Measurement – pojedynczy pomiar temperatury."""

from __future__ import annotations

from datetime import datetime

from model.parsing import DATE_FORMAT, parse_value


class Measurement:
    """Pojedynczy pomiar temperatury w °C."""

    def __init__(self, location: str, measured_at: datetime, value: float) -> None:
        """Tworzy pomiar, walidując wszystkie trzy atrybuty."""
        if not isinstance(location, str) or not location.strip():
            raise ValueError("Lokalizacja nie może być pusta.")
        if not isinstance(measured_at, datetime):
            raise ValueError("Czas pomiaru musi być obiektem datetime.")
        self.location: str = location.strip()
        self.measured_at: datetime = measured_at
        self.value: float = parse_value(value)

    def __str__(self) -> str:
        """Zwraca opis w postaci 'Warszawa, 2024-10-07 12:00, 18.5 °C'."""
        return f"{self.location}, {self.measured_at.strftime(DATE_FORMAT)}, {self.value} °C"

    def __repr__(self) -> str:
        return (
            f"Measurement({self.location!r}, "
            f"{self.measured_at.strftime(DATE_FORMAT)!r}, {self.value!r})"
        )
