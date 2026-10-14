# Pomysły na rozwój ClipMaker

## Najpierw: niezawodność

- [ ] **Usunąć obejście zależności MoviePy/Pillow.** Obecny MoviePy 2.2.1 deklaruje Pillow `<12`, a Python 3.15 wymaga nowszego gotowego pakietu na Windows. Śledzić wydanie MoviePy zgodne z Pillow 12+, wtedy usunąć `override-dependencies` z `pyproject.toml` i ponownie uruchomić testy renderowania.
- [ ] **Dodać CI na GitHub Actions.** Na Windows i Linux uruchamiać `uv sync --locked` oraz `uv run python -m unittest discover -s tests -v`. Zapobiegnie to publikacji zmian psujących renderowanie. [Instrukcja uv dla GitHub Actions](https://docs.astral.sh/uv/guides/integration/github/).
- [ ] **Rozszerzyć walidację wejścia.** Sprawdzać wszystkie zakresy wideo i audio przed rozpoczęciem eksportu, czytelnie zgłaszać brak ścieżki audio w pliku wideo i zapobiegać zapisowi na pliku źródłowym.
- [ ] **Dodać testy dla większej liczby wejść.** Kilka filmów, plik wideo jako źródło dźwięku, niepoprawne zakresy i media bez ścieżki audio.

## Następnie: wygoda i jakość filmu

- [ ] **Wybór dopasowania obrazu.** Dodać `fit` (pasy), `crop` (wypełnienie kadru) i obecny `stretch`. Domyślna opcja powinna zachowywać proporcje, szczególnie dla formatu pionowego.
- [ ] **Ustawienia eksportu w JSON.** Udostępnić FPS, kodek, jakość/bitrate i liczbę wątków z sensownymi wartościami domyślnymi.
- [ ] **Przyjazne CLI.** Dodać `--check` do sprawdzania konfiguracji bez renderowania oraz `--output` do nadpisania ścieżki wyniku. Umożliwić ścieżki mediów względem katalogu pliku konfiguracyjnego.
- [ ] **Szablon konfiguracji.** Dodać `config.example.json` z względnymi ścieżkami; prywatne ścieżki plików trzymać poza repozytorium.

## Później: funkcje twórcze

- [ ] **Przejścia między ujęciami.** Zacząć od przenikania z konfigurowalną długością. MoviePy udostępnia kompozycję klipów i efekty przejść: [dokumentacja](https://zulko.github.io/moviepy/user_guide/compositing.html).
- [ ] **Napisy i plansze tytułowe.** Tekst, czcionka, pozycja oraz zakres czasu zapisane w konfiguracji.
- [ ] **Kilka proporcji eksportu.** Presety 9:16, 16:9 i 1:1 oraz możliwość utworzenia kilku wersji z tej samej osi czasu.
- [ ] **Podgląd przed pełnym eksportem.** Render krótkiego fragmentu lub pojedynczych klatek, aby szybko sprawdzić kadrowanie i napisy.
