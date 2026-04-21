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

### External API Integration (Mandatory)
When implementing any client that connects to an external API:
1. **Research the official API documentation first** — do not guess endpoints, auth, rate limits, or response formats
2. Use Gemini CLI to fetch documentation if official docs are not locally available
3. Document the API specification in `src/data/api_specs/{service_name}.md` before writing any client code
4. Verify: base URL, authentication method, endpoint paths, rate limits, pagination, response schema, error codes
5. Implementation must match the documented specification — no assumed behavior

This applies to: exchange APIs, broker APIs, notification services (Discord, LINE, Telegram), data providers, and any other external HTTP/WebSocket service.

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
