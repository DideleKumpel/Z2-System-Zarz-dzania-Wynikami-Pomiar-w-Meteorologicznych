# System Zarządzania Wynikami Pomiarów Meteorologicznych

Program konsolowy w Pythonie do przechowywania, zapisywania (CSV) i analizowania
pomiarów temperatury (°C) w różnych lokalizacjach. Projekt realizuje zakres na
ocenę 5 z rozszerzeniem **A – tabela i sortowanie wyników (pandas)**.

## Wymagania

- Python **3.10 lub nowszy** (testowane na Pythonie 3.13)
- biblioteki z `requirements.txt`: numpy, pandas, pytest

## Instalacja i uruchomienie (Windows / PowerShell)

```powershell
cd "Z2-System Zarządzania Wynikami Pomiarów Meteorologicznych"
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

Linux / macOS: `python3 -m venv .venv && source .venv/bin/activate`, dalej tak samo.
Katalog `.venv` nie jest częścią oddawanego projektu.

## Struktura projektu

| Plik | Zawartość |
|------|-----------|
| `model/` | pakiet: `measurement.py` (`Measurement`), `weather_data.py` (`WeatherData`), `parsing.py` (stałe i funkcje parsujące) – walidacja, filtrowanie, średnia, zapis/odczyt CSV (bez `input()`/`print()`) |
| `analysis.py` | `TemperatureMatrix` – macierz NumPy (lokalizacje × dni), średnie dzienne, maksimum |
| `table.py` | rozszerzenie A – tabela pandas i sortowanie |
| `ui.py` | menu konsolowe i obsługa błędów |
| `main.py` | punkt wejścia (`python main.py`); import modułów nie uruchamia menu |
| `dane_pomiarowe.csv` | przykładowy poprawny plik CSV |
| `tests/` | testy automatyczne (pytest) |

## Menu

```
1. Dodaj nowy pomiar
2. Wyświetl pomiary dla lokalizacji
3. Oblicz średnią temperaturę dla lokalizacji
4. Zapisz pomiary do pliku
5. Wczytaj pomiary z pliku
6. Wyświetl średnie temperatury dla kolejnych dni
7. Wyświetl maksimum w macierzy średnich dziennych
8. Wyjdź
9. Wyświetl tabelę pomiarów z sortowaniem (pandas)
```

Każdy błąd (złe dane, nieznana opcja, brak pomiarów, błąd pliku, niepełna macierz)
wyświetla komunikat, a program działa dalej. Temperaturę można wpisać z kropką
lub przecinkiem (`18.5` / `18,5`). Średnie są wyświetlane z dokładnością do dwóch
miejsc po przecinku, obliczenia nie zaokrąglają wyników pośrednich.

## Najważniejsze decyzje projektowe

- Lokalizacje porównywane są po usunięciu skrajnych spacji i bez rozróżniania
  wielkości liter (`" warszawa "` = `"Warszawa"`). Para lokalizacja + czas jest unikalna.
- Data ma ściśle format `RRRR-MM-DD HH:MM`; niemożliwe daty (np. 2024-02-30) są odrzucane.
- Temperatura musi być skończoną liczbą: NaN i nieskończoność są odrzucane, wartości ujemne dozwolone.
- Każda niepoprawna operacja zgłasza `ValueError` i nie zmienia stanu.
- `load_from_file` najpierw wczytuje cały plik do tymczasowego obiektu, a dopiero po
  pełnej walidacji zastępuje pomiary. Błąd rekordu podaje numer wiersza pliku.
  Brak pliku / brak dostępu → `OSError` (np. `FileNotFoundError`).
- `TemperatureMatrix.from_weather_data` budowana jest od nowa przy każdej analizie
  (opcje 6 i 7), więc uwzględnia aktualne dane. Lokalizacje sortowane są alfabetycznie
  z uwzględnieniem polskich liter (Kraków < Łódź < Warszawa), dni chronologicznie.
  Kilka pomiarów w jednym dniu jest uśrednianych do jednej komórki. Brakująca para
  lokalizacja–dzień powoduje `ValueError` z listą braków (braki nie są zastępowane zerem).

## Rozszerzenie A – tabela i sortowanie (pandas)

Funkcja `measurements_table(data, sort_by=None, ascending=True)` w `table.py` zwraca
`pandas.DataFrame` z kolumnami **lokalizacja**, **data i godzina**, **temperatura**.

- `sort_by=None` – kolejność dodania, `"czas"` – po czasie, `"temperatura"` – po temperaturze;
  `ascending=True/False` – rosnąco/malejąco.
- Remisy rozstrzygane są po lokalizacji (alfabetycznie), a następnie po czasie (rosnąco).
  Sortowanie stabilne (`mergesort`) po trzech kluczach jednocześnie.
- Tabela budowana jest jako nowa kopia danych, więc sortowanie **nie zmienia**
  `WeatherData.measurements`.
- Pusty zbiór daje pustą tabelę z tymi samymi kolumnami (w menu: „Brak pomiarów do wyświetlenia”).

W menu: opcja **9**, następnie wybór `0` (bez sortowania), `1` (czas) lub `2` (temperatura)
i kolejność `r` (rosnąco) / `m` (malejąco).

Testy rozszerzenia: `tests/test_table.py` (kolejność rosnąco/malejąco, remisy,
pusty zbiór, niezmienność danych źródłowych).

## Testy

```powershell
python -m pytest            # wszystkie testy
python -m pytest -v tests/test_table.py   # tylko rozszerzenie A
```

| Plik | Co sprawdza |
|------|-------------|
| `tests/test_model.py` | dodawanie i filtrowanie (`" warszawa "` → 2 pomiary chronologicznie), walidacja (pusta lokalizacja, niemożliwa data, tekst, NaN, ±inf, duplikat – bez zmiany stanu), średnia (10.0 i 14.0 → 12.0, nieznana lokalizacja → `ValueError`) |
| `tests/test_files.py` | zapis i odczyt z polskimi znakami, zastępowanie zbioru, plik z samym nagłówkiem → pusty zbiór, błędne pliki (nagłówek, rekord, data, wartość, duplikat) → `ValueError` z numerem wiersza bez zmiany stanu, nieistniejący plik → `FileNotFoundError` |
| `tests/test_matrix.py` | macierz z przykładu: Kraków `[16.5, 18.0]`, Warszawa `[18.5, 20.0]`, średnie `[17.5, 19.0]`, maksimum `20.0`; agregacja dnia (10.0 i 14.0 → 12.0); brak pary lokalizacja–dzień i pusty zbiór → `ValueError` |
| `tests/test_table.py` | rozszerzenie A |
| `tests/test_ui.py` | przykładowa sesja menu, kontynuacja pracy po błędach, import nie uruchamia menu |

Wyniki porównywane są z tolerancją 10⁻⁶. Testy używają plików tymczasowych (`tmp_path`).

### Wynik testów

```
63 passed
```

## Wyniki scenariuszy z sekcji „Sprawdzenie poprawności”

- **Dodanie i filtrowanie** – po dodaniu dwóch pomiarów Warszawy i jednego Krakowa
  wyszukiwanie `" warszawa "` zwraca tylko dwa pomiary Warszawy, od najwcześniejszego.
- **Walidacja** – pusta lokalizacja, niemożliwa data, nieliczbowa temperatura, NaN,
  nieskończoność i duplikat dają komunikat błędu; liczba pomiarów się nie zmienia.
- **Zapis i odczyt** – po zapisie i ponownym wczytaniu lokalizacje (także `Łódź`),
  czasy i wartości są identyczne; wczytanie zastępuje poprzedni zbiór.
- **Błędny plik** nie zmienia danych; plik z samym nagłówkiem daje pusty zbiór;
  nieistniejący plik daje komunikat „Błąd pliku”.
- **Analiza dzienna** – dla danych z przykładu opcja 6 wyświetla `2024-10-07: 17.50 °C`
  i `2024-10-08: 19.00 °C`, a opcja 7 `20.00 °C`.

Przykładowy plik `dane_pomiarowe.csv` zawiera dane z przykładu oraz Łódź z dwoma
pomiarami 2024-10-07 (14.0 i 16.0 → średnia dnia 15.0). Po jego wczytaniu opcja 6 daje
`2024-10-07: 16.67 °C`, `2024-10-08: 18.50 °C`, a opcja 7 `20.00 °C`.
