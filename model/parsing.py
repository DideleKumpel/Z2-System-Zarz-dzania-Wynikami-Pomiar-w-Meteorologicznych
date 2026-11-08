"""Stałe formatu danych oraz funkcje parsujące i normalizujące."""

from __future__ import annotations

import math
import re
from datetime import datetime
from numbers import Real

DATE_FORMAT = "%Y-%m-%d %H:%M"
CSV_HEADER = ["location", "measured_at", "value"]
_DATE_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}")


def normalize_location(location: str) -> str:
    """Zwraca klucz lokalizacji: bez skrajnych spacji, bez rozróżniania wielkości liter."""
    return location.strip().casefold()


_POLISH_ORDER = str.maketrans({
    "ą": "a\ufffe", "ć": "c\ufffe", "ę": "e\ufffe", "ł": "l\ufffe", "ń": "n\ufffe",
    "ó": "o\ufffe", "ś": "s\ufffe", "ź": "z\ufffe", "ż": "z\uffff",
})


def location_sort_key(location: str) -> str:
    """Zwraca klucz sortowania alfabetycznego z uwzględnieniem polskich liter (np. K < Ł < W)."""
    return normalize_location(location).translate(_POLISH_ORDER)


def parse_datetime(text: str) -> datetime:
    """Parsuje datę w formacie RRRR-MM-DD HH:MM; błędny format powoduje ValueError."""
    if not isinstance(text, str):
        raise ValueError("Data musi być tekstem w formacie RRRR-MM-DD HH:MM.")
    text = text.strip()
    if not _DATE_PATTERN.fullmatch(text):
        raise ValueError(f"Niepoprawny format daty: '{text}' (wymagany RRRR-MM-DD HH:MM).")
    try:
        return datetime.strptime(text, DATE_FORMAT)
    except ValueError:
        raise ValueError(f"Niemożliwa data lub godzina: '{text}'.") from None


def parse_value(value: object) -> float:
    """Zamienia wartość na skończoną liczbę float; NaN, nieskończoność i tekst nieliczbowy są odrzucane."""
    if isinstance(value, bool):
        raise ValueError("Temperatura musi być liczbą.")
    if isinstance(value, str):
        text = value.strip()
        try:
            number = float(text)
        except ValueError:
            raise ValueError(f"Temperatura musi być liczbą, otrzymano: '{value}'.") from None
    elif isinstance(value, Real):
        number = float(value)
    else:
        raise ValueError("Temperatura musi być liczbą.")
    if not math.isfinite(number):
        raise ValueError("Temperatura musi być skończoną liczbą (bez NaN i nieskończoności).")
    return number

