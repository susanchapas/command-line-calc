# Command-Line Calculator

An enhanced REPL calculator built around classic design patterns. It supports
addition, subtraction, multiplication, division, power, and root operations,
keeps a `pandas`-backed history that auto-saves to CSV, and offers undo/redo
plus a small set of built-in commands.

## Requirements

- Python 3.10 or newer

## Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the project and test dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -e '.[test]'
```

## Run the calculator

```bash
calculator
```

You can also run it directly:

```bash
python -m calculator.main
```

## Usage

At the `>` prompt, run a calculation by typing an operation and two numbers:

```
> add 2 3
Result: 2 + 3 = 5
> power 2 10
Result: 2 ^ 10 = 1024
> root 27 3
Result: 27 √ 3 = 3
```

### Commands

| Command | Description |
| --- | --- |
| `<operation> <a> <b>` | run a calculation (`add`, `subtract`, `multiply`, `divide`, `power`, `root`) |
| `history` | show the calculation history |
| `undo` / `redo` | step backward or forward through history |
| `save [path]` | save history to a CSV file |
| `load [path]` | load history from a CSV file |
| `clear` | erase the current history |
| `help` | list commands and operations |
| `exit` | quit (`quit` and `q` also work) |

## Configuration

Settings are read from the environment (and an optional `.env` file via
`python-dotenv`). Copy `.env.example` to `.env` to customize them:

| Variable | Default | Meaning |
| --- | --- | --- |
| `CALCULATOR_HISTORY_FILE` | `calculator_history.csv` | CSV file used for auto-save/load |
| `CALCULATOR_AUTO_SAVE` | `true` | persist history after each calculation |
| `CALCULATOR_MAX_HISTORY` | `100` | maximum number of stored calculations |

Invalid values (e.g. a non-numeric `CALCULATOR_MAX_HISTORY`) are rejected at
startup with a clear message.

## Design

The application is organized around the patterns the assignment calls for:

- **Strategy** (`strategies.py`) — interchangeable operation execution objects.
- **Factory** (`factory.py`) — builds a strategy from an operation name.
- **Observer** (`observers.py`) — logging and CSV auto-save react to each calculation.
- **Memento** (`memento.py`) — snapshots power `undo`/`redo`.
- **Facade** (`calculator.py`) — the `Calculator` class hides these subsystems
  and the `pandas` history behind a small interface used by the REPL.

Error handling uses both **LBYL** (validating configuration and checking for an
existing history file before loading) and **EAFP** (executing operations and
parsing numbers inside `try`/`except`).

## Run Tests

Branch coverage is enabled in `pyproject.toml`, so this command enforces 100%
of both lines and branches:

```bash
python -m pytest --cov=calculator --cov-report=term-missing --cov-fail-under=100
```

### Coverage exceptions

`# pragma: no cover` is used only for code that cannot be exercised by the test
suite, such as the module entry-point guard in `src/calculator/main.py`.
