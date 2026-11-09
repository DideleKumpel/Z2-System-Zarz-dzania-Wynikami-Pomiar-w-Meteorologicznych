# System Zarządzania Wynikami Pomiarów Meteorologicznych

## Wersja Pythona

Python 3.10 lub nowszy (sprawdzone na Pythonie 3.13).

## Uruchomienie

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

Przykładowy poprawny plik CSV: `dane_pomiarowe.csv`.

## Wyniki scenariuszy sprawdzających

- **Dodanie i filtrowanie** – dla dwóch pomiarów Warszawy i jednego Krakowa wyszukiwanie
  `" warszawa "` zwraca tylko dwa pomiary Warszawy w kolejności czasu.
- **Walidacja** – pusta lokalizacja, niemożliwa data, nieliczbowa temperatura, NaN,
  nieskończoność i duplikat są odrzucane bez zmiany danych.
- **Zapis i odczyt** – po pełnym cyklu lokalizacje (także z polskimi znakami), czasy
  i wartości są zachowane; poprawne wczytanie zastępuje poprzedni zbiór.
- **Błędny plik** nie zmienia stanu; plik z samym nagłówkiem daje pusty zbiór;
  nieistniejący plik zgłasza `FileNotFoundError`.
- **Średnia** – dla 10.0 i 14.0 wynik to 12.0; nieznana lokalizacja → `ValueError`.
- **Macierz** – Kraków `[16.5, 18.0]`, Warszawa `[18.5, 20.0]`, średnie dzienne
  `[17.5, 19.0]`, maksimum `20.0`. Wartości 10.0 i 14.0 w jednym dniu dają komórkę 12.0.
  Brak lokalizacji w którymś dniu i pusty zbiór → `ValueError`.

## Rozszerzenie A – tabela i sortowanie (pandas)

Funkcja `measurements_table(data, sort_by=None, ascending=True)` w `table.py` zwraca
`pandas.DataFrame` z kolumnami **lokalizacja**, **data i godzina**, **temperatura**.

- `sort_by`: `None` (kolejność dodania), `"czas"` lub `"temperatura"`;
  `ascending=True/False` – rosnąco/malejąco.
- Remisy rozstrzygane są po lokalizacji, a następnie po czasie.
- Tabela jest tworzona z kopii danych, więc sortowanie nie zmienia `measurements`.
- Pusty zbiór daje pustą tabelę.

**Uruchomienie:** w menu opcja **9**, następnie wybór sortowania `0` (brak), `1` (czas)
lub `2` (temperatura) i kolejności `r` (rosnąco) / `m` (malejąco).
