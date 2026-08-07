# Command-Line Calculator

An enhanced REPL calculator built around classic design patterns. It supports
ten two-operand arithmetic operations, keeps a `pandas`-backed history that
auto-saves to CSV, and offers undo/redo plus a small set of built-in commands.

## Requirements

- Python 3.10 or newer

## Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Run the calculator

```bash
python -m app.main
```

Installing the project (`python -m pip install -e .`) also provides a
`calculator` command that does the same thing.

## Usage

At the `>` prompt, run a calculation by typing an operation and two numbers:

```
> add 2 3
Result: 2 + 3 = 5
> power 2 10
Result: 2 ^ 10 = 1024
> root 27 3
Result: 27 √ 3 = 3
> percentage 25 200
Result: 25 %of 200 = 12.5
```

### Operations

| Operation | Symbol | Result of `<a> <b>` |
| --- | --- | --- |
| `add` | `+` | a plus b |
| `subtract` | `-` | a minus b |
| `multiply` | `*` | a times b |
| `divide` | `/` | a divided by b |
| `power` | `^` | a raised to the power of b |
| `root` | `√` | the bth root of a |
| `modulus` | `%` | the remainder of a divided by b |
| `int_divide` | `//` | a divided by b, fractional part discarded |
| `percentage` | `%of` | a as a percentage of b, `(a / b) * 100` |
| `abs_diff` | `\|Δ\|` | the absolute difference between a and b |

### Commands

| Command | Description |
| --- | --- |
| `<operation> <a> <b>` | run a calculation (see the operations table above) |
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

## Project structure

```
command-line-calculator/
├── app/
│   ├── __init__.py
│   ├── calculation.py
│   ├── calculator.py
│   ├── calculator_config.py
│   ├── calculator_memento.py
│   ├── cli.py
│   ├── exceptions.py
│   ├── factory.py
│   ├── history.py
│   ├── input_validators.py
│   ├── logger.py
│   ├── main.py
│   ├── observers.py
│   ├── operations.py
│   └── strategies.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_*.py
├── .env
├── .env.example
├── requirements.txt
├── pyproject.toml
├── README.md
└── .github/
    └── workflows/
        └── python-app.yml
```

## Design

The application is organized around the patterns the assignment calls for:

- **Strategy** (`strategies.py`) — interchangeable operation execution objects.
- **Factory** (`factory.py`) — builds a strategy from an operation name.
- **Observer** (`observers.py`) — logging and CSV auto-save react to each calculation.
- **Memento** (`calculator_memento.py`) — snapshots power `undo`/`redo`.
- **Facade** (`calculator.py`) — the `Calculator` class hides these subsystems
  and the `pandas` history behind a small interface used by the REPL.

Supporting modules: `exceptions.py` holds the error hierarchy (every raised
error derives from `CalculatorError`), `input_validators.py` parses REPL
operands, `logger.py` centralizes logging setup, and `calculator_config.py`
loads settings from the environment.

Error handling uses both **LBYL** (validating configuration and checking for an
existing history file before loading) and **EAFP** (executing operations and
parsing numbers inside `try`/`except`).

## Run Tests

Branch coverage is enabled in `pyproject.toml`, so this command enforces 100%
of both lines and branches:

```bash
python -m pytest --cov=app --cov-report=term-missing --cov-fail-under=100
```

### Coverage exceptions

`# pragma: no cover` is used only for code that cannot be exercised by the test
suite, such as the module entry-point guard in `app/main.py`.
