# ClipMaker

ClipMaker składa plik MP4 z obrazów, fragmentów wideo i ścieżki dźwiękowej.

## Uruchomienie

```powershell
uv sync
uv run python -m clip_maker config.json
```

Program domyślnie czyta `config.json` z bieżącego katalogu. Można podać inną ścieżkę jako argument. W pliku znajdują się obecnie ścieżki z innego komputera (`C:\Users\Daric\...`); przed uruchomieniem na tym komputerze trzeba je zastąpić istniejącymi plikami.

Przykładowa struktura konfiguracji:

```json
{
  "media_files": ["intro.mp4", "photo1.jpg", "photo2.jpg"],
  "clip_size": [554, 860],
  "media_time_schedule": [[0, 2.92], 2],
  "audio_file": "music.mp3",
  "audio_time": [20, 27],
  "result_file": "output.mp4"
}
```

Każdy film w `media_files` wymaga zakresu `[start, end]` w sekundach. Każdy obraz poza ostatnim wymaga liczby sekund. Ostatni obraz wypełnia resztę wybranego dźwięku. Jeśli ostatnim plikiem jest film, podaj także jego zakres; zostanie przycięty do końca dźwięku, o ile jest za długi. `audio_time` jest opcjonalne i pominięcie tej wartości oznacza użycie całego dźwięku.

## Kierunki rozwoju

- Obsługa proporcji obrazu: obecnie obraz jest rozciągany do `clip_size`; warto dodać tryby przycięcia i pasów.
- Parametry eksportu w konfiguracji: FPS, kodek, jakość oraz liczba wątków są na stałe w kodzie.
- Przejścia i napisy, najlepiej jako osobne opcjonalne kroki osi czasu.
- Pasek postępu i czytelniejszy raport błędów dla uruchomienia z terminala.
