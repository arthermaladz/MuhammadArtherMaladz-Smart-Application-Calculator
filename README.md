# Arther Smart Calculator

A portable Windows desktop calculator built with Python 3.11+ and Tkinter. The app has no runtime third-party dependencies and does not use the network.

## Run from source

```powershell
python src\main.py
```

## Features

- Standard and scientific expression entry with live preview, keyboard input, `ans`, contextual percentages, implicit multiplication, and bounded factorial/power operations.
- Decimal arithmetic and a restricted Python AST evaluator; user input is never passed to `eval`.
- Persistent calculation history, settings, memory buttons, themes, angle units, and always-on-top toggle.
- Offline conversion for length, mass, volume, area, speed, time, and temperature; discount/tax calculator.
- Portable settings and SQLite history under `data\` next to the source project or executable.

On a read-only location the app continues to calculate and reports persistence errors in its status line.

## Tests

```powershell
python -m unittest discover -s tests -v
```

The test suite includes over 100 arithmetic input combinations and checks the core acceptance cases.

## Build the portable Windows executable

Run on Windows with a 64-bit Python installation:

```powershell
python -m pip install -r requirements.txt
python -m PyInstaller --clean --noconfirm --onefile --windowed --name ArtherSmartCalculator --add-data "README.md;." src\main.py
```

The executable is written to `dist\ArtherSmartCalculator.exe`. Start it once to create a `data\` folder alongside the executable. Keep that folder with the executable when moving the app.

# MuhammadArtherMaladz-Smart-Application-Calculator
