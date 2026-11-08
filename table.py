"""Rozszerzenie A: tabela pomiarów (pandas) i sortowanie wyników."""

from __future__ import annotations

import pandas as pd

from model import DATE_FORMAT, WeatherData, location_sort_key

COLUMNS = ["lokalizacja", "data i godzina", "temperatura"]
SORT_KEYS = {"czas": "data i godzina", "temperatura": "temperatura"}


def measurements_table(
    data: WeatherData, sort_by: str | None = None, ascending: bool = True
) -> pd.DataFrame:
    """Zwraca tabelę pomiarów jako DataFrame, opcjonalnie posortowaną.

    sort_by: None (kolejność dodania), "czas" albo "temperatura".
    Remisy rozstrzygane są po lokalizacji (alfabetycznie, bez rozróżniania wielkości liter),
    a następnie po czasie, zawsze rosnąco. Lista data.measurements nie jest zmieniana.
    """
    if sort_by is not None and sort_by not in SORT_KEYS:
        raise ValueError(f"Nieznany klucz sortowania: '{sort_by}' (dozwolone: czas, temperatura).")

    frame = pd.DataFrame(
        [(m.location, m.measured_at, m.value) for m in data.measurements],
        columns=COLUMNS,
    )
    frame["temperatura"] = frame["temperatura"].astype(float)
    frame["data i godzina"] = pd.to_datetime(frame["data i godzina"])
    if sort_by is None or frame.empty:
        return frame.reset_index(drop=True)

    frame["_loc_key"] = frame["lokalizacja"].map(location_sort_key)
    primary = SORT_KEYS[sort_by]
    frame = frame.sort_values(
        by=[primary, "_loc_key", "data i godzina"],
        ascending=[ascending, True, True],
        kind="mergesort",
    )
    return frame.drop(columns="_loc_key").reset_index(drop=True)


def format_table(frame: pd.DataFrame) -> str:
    """Zwraca tabelę jako tekst do wyświetlenia w konsoli."""
    if frame.empty:
        return "Brak pomiarów do wyświetlenia."
    shown = frame.copy()
    shown["data i godzina"] = shown["data i godzina"].dt.strftime(DATE_FORMAT)
    shown["temperatura"] = shown["temperatura"].map(lambda v: f"{v:.2f} °C")
    return shown.to_string(index=False)
