# Command-Line Calculator

A small Python calculator that runs in a REPL and supports addition, subtraction, multiplication, and division.

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
python -m pip install -e .[test]
```

## Run the calculator

Start the REPL with the installed console script:

```bash
calculator
```

You can also run it directly:

```bash
python -m calculator.main
```

## Usage

1. Choose an operation: `add`, `subtract`, `multiply`, or `divide`.
2. Enter the first number.
3. Enter the second number.
4. Read the result and continue or type `quit` to exit.

The calculator validates the operation name and numbers, and it handles division by zero with a clear message.

## Run Tests

```bash
python -m pytest --cov=calculator --cov-report=term-missing --cov-fail-under=100
```
