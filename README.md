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
> percent 25 200
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
| `percent` | `%of` | a as a percentage of b, `(a / b) * 100` |
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

```bash
cp .env.example .env
```

**Base directories** — created on startup if they do not exist:

| Variable | Default | Meaning |
| --- | --- | --- |
| `CALCULATOR_LOG_DIR` | `logs` | directory for log files |
| `CALCULATOR_HISTORY_DIR` | `history` | directory for history files |

**History settings:**

| Variable | Default | Meaning |
| --- | --- | --- |
| `CALCULATOR_MAX_HISTORY_SIZE` | `100` | maximum number of stored calculations |
| `CALCULATOR_AUTO_SAVE` | `true` | persist history after each calculation |

**Calculation settings:**

| Variable | Default | Meaning |
| --- | --- | --- |
| `CALCULATOR_PRECISION` | `10` | decimal places each result is rounded to |
| `CALCULATOR_MAX_INPUT_VALUE` | `1e12` | largest accepted operand magnitude |
| `CALCULATOR_DEFAULT_ENCODING` | `utf-8` | encoding for the log and history files |

**File names**, resolved inside the directories above:

| Variable | Default | Meaning |
| --- | --- | --- |
| `CALCULATOR_LOG_FILE` | `calculator.log` | file each calculation is logged to |
| `CALCULATOR_HISTORY_FILE` | `calculator_history.csv` | CSV file used for auto-save/load |

So the defaults put the log at `logs/calculator.log` and the history at
`history/calculator_history.csv`. Giving either file name as an absolute path
overrides its base directory.

Every value is parsed and validated when the application starts, so invalid
configuration (a non-numeric `CALCULATOR_MAX_HISTORY_SIZE`, a negative
`CALCULATOR_PRECISION`, an unknown `CALCULATOR_DEFAULT_ENCODING`) is reported
immediately with a `ConfigError` message rather than failing later. Any
variable that is not set falls back to the default in the tables above, so the
application runs with no `.env` file at all.

## Logging

`logger.py` configures the standard library `logging` module on startup. The
log file is `CALCULATOR_LOG_DIR/CALCULATOR_LOG_FILE` and is written with
`CALCULATOR_DEFAULT_ENCODING`; each line carries a timestamp, level, and
message:

```
2026-08-07 09:31:53,261 INFO calculator: Calculation: add(2, 3) = 5
2026-08-07 09:31:53,262 WARNING calculator: Rejected 'divide 1 0': Cannot divide by zero.
2026-08-07 09:31:53,263 ERROR calculator: Save failed: Could not write /nope/out.csv
```

| Level | Used for |
| --- | --- |
| `INFO` | startup and shutdown, the effective configuration, every calculation, and each history change (undo, redo, clear, save, load) |
| `WARNING` | input the calculator refused — bad operands, unknown operations, unknown commands |
| `ERROR` | failures the user cannot correct by retyping — invalid configuration, and history files that cannot be read or written |

The file records everything from `INFO` up. The console handler is held to
`WARNING` so the REPL shows only problems and its own output stays readable;
the full detail is always in the log file.

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
operands and range-checks them against `CALCULATOR_MAX_INPUT_VALUE`,
`logger.py` centralizes logging setup, and `calculator_config.py` loads and
validates settings from the environment.

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
