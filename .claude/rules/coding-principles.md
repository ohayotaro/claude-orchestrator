# Coding Principles

## Python

### Type Safety
- **Type hints mandatory**: All function arguments and return values must have type annotations
- **mypy strict**: Must pass type checking with `--strict` mode
- Consider `Decimal` for financial calculations (avoid floating-point precision issues)

### Code Quality
- **ruff**: Linter + formatter
- **Docstrings**: Mandatory for public functions and classes (Google style)
- **Test coverage**: 80% minimum
- **Function length**: Target under 50 lines
- **Class responsibility**: Single Responsibility Principle

### Naming Conventions
```python
# Variables and functions: snake_case
def calculate_sharpe_ratio(returns: pd.Series) -> float: ...

# Classes: PascalCase
class MovingAverageCrossover(Strategy): ...

# Constants: UPPER_SNAKE_CASE
MAX_DRAWDOWN_THRESHOLD = 0.20

# Private: _prefix
def _validate_data(self) -> None: ...
```

### Dependencies
- Package manager: **uv**
- Dependencies managed in `pyproject.toml`
- Version pinning via `uv.lock`
- Do not add unnecessary dependencies

## MQL5

### Fundamentals
- Always use `#property strict`
- Error handling: check `GetLastError()` after every API call
- Memory management: `ArrayFree()` dynamic arrays after use
- Magic numbers: set unique value per EA

### Structure
```mql5
// Header: property definitions
#property copyright "..."
#property version   "1.00"
#property strict

// Input parameters
input int    InpMagicNumber = 12345;
input double InpLotSize     = 0.01;
input int    InpStopLoss    = 50;

// Minimal global variables
CTrade trade;

// Initialization
int OnInit() { ... }

// Main logic
void OnTick() { ... }

// Cleanup
void OnDeinit(const int reason) { ... }
```
