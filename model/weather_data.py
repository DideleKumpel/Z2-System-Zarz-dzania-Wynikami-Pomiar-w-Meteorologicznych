"""Klasa WeatherData – zbiór pomiarów z zapisem/odczytem CSV."""

from __future__ import annotations

import csv
from datetime import datetime

from model.measurement import Measurement
from model.parsing import CSV_HEADER, DATE_FORMAT, normalize_location, parse_datetime


class WeatherData:
    """Zbiór pomiarów temperatury."""

    def __init__(self) -> None:
        """Tworzy pusty zbiór pomiarów."""
        self.measurements: list[Measurement] = []

    @staticmethod
    def _key(measurement: Measurement) -> tuple[str, datetime]:
        return normalize_location(measurement.location), measurement.measured_at

    def add_measurement(self, location: str, measured_at: str, value: float) -> None:
        """Waliduje dane, parsuje datę (RRRR-MM-DD HH:MM) i dodaje pomiar.

        Zgłasza ValueError dla niepoprawnych danych lub duplikatu (lokalizacja + czas).
        """
        measurement = Measurement(location, parse_datetime(measured_at), value)
        key = self._key(measurement)
        if any(self._key(m) == key for m in self.measurements):
            raise ValueError(
                f"Pomiar dla lokalizacji '{measurement.location}' o czasie "
                f"{measurement.measured_at.strftime(DATE_FORMAT)} już istnieje."
            )
        self.measurements.append(measurement)

    def get_measurements_by_location(self, location: str) -> list[Measurement]:
        """Zwraca pomiary danej lokalizacji w kolejności chronologicznej (może być pusta lista)."""
        key = normalize_location(location)
        found = [m for m in self.measurements if normalize_location(m.location) == key]
        return sorted(found, key=lambda m: m.measured_at)

    def get_average_temperature(self, location: str) -> float:
        """Zwraca średnią temperaturę lokalizacji; brak pomiarów powoduje ValueError."""
        found = self.get_measurements_by_location(location)
        if not found:
            raise ValueError(f"Brak pomiarów dla lokalizacji '{location.strip()}'.")
        return sum(m.value for m in found) / len(found)

    def save_to_file(self, filename: str) -> None:
        """Zapisuje wszystkie pomiary do pliku CSV (UTF-8, nagłówek, nadpisuje plik)."""
        with open(filename, "w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(CSV_HEADER)
            for m in self.measurements:
                writer.writerow([m.location, m.measured_at.strftime(DATE_FORMAT), repr(m.value)])

    def load_from_file(self, filename: str) -> None:
        """Wczytuje i waliduje cały plik CSV; poprawny odczyt zastępuje dotychczasowe pomiary.

        Błędy treści pliku zgłaszane są jako ValueError (z numerem wiersza),
        błędy dostępu jako OSError. W razie błędu stan obiektu się nie zmienia.
        """
        loaded = WeatherData()
        try:
            with open(filename, "r", encoding="utf-8", newline="") as file:
                reader = csv.reader(file)
                header = next(reader, None)
                if header is None:
                    raise ValueError("Plik jest pusty: brak nagłówka location,measured_at,value.")
                if header and header[0].startswith("﻿"):
                    header[0] = header[0][1:]
                if [h.strip() for h in header] != CSV_HEADER:
                    raise ValueError(
                        "Wiersz 1: niepoprawny nagłówek, oczekiwano location,measured_at,value."
                    )
                for row in reader:
                    line = reader.line_num
                    if not row:
                        continue  # pusta linia
                    if len(row) != 3:
                        raise ValueError(
                            f"Wiersz {line}: oczekiwano 3 pól, otrzymano {len(row)}."
                        )
                    try:
                        loaded.add_measurement(row[0], row[1], row[2])
                    except ValueError as error:
                        raise ValueError(f"Wiersz {line}: {error}") from None
        except UnicodeDecodeError:
            raise ValueError("Plik nie jest poprawnie zakodowany w UTF-8.") from None
        except csv.Error as error:
            raise ValueError(f"Niepoprawny format CSV: {error}") from None
        self.measurements = loaded.measurements
