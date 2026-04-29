---
name: data-pipeline
description: Build and manage market data acquisition, normalization, and storage pipelines. Begins with mandatory API specification research before any implementation.
agent: data-engineer
context: fork
allowed-tools: "Bash(python *) Bash(uv *) Bash(codex *) Bash(gemini *) Read Write Edit Glob Grep"
---

# Data Pipeline Builder

Build market data fetching, cleaning, and storage pipelines.

**Mandatory constraint**: No implementation may begin until the target API's specification has been researched and documented (Step 2).

## Workflow

### Step 1: Requirements Gathering
Ask the user:
1. Target market and instruments (e.g., BTC/USDT, EUR/USD, AAPL)
2. Timeframe (1m, 5m, 15m, 1h, 4h, 1d)
3. Date range (start, end)
4. Data source (select from project's configured sources, or specify custom API)
5. Data types needed (OHLCV, tick, order book, funding rate, financial statements)

### Step 2: API Specification Research (MANDATORY)

**This step must be completed before any code is written.**

Using Gemini CLI or Opus subagent, research the actual API documentation:

```bash
gemini -p "Research the API specification for {data_source}:

1. BASE URL: What is the REST API base URL?
2. AUTHENTICATION: What auth method is required (API key header, HMAC signature, OAuth, none)?
3. ENDPOINTS: Which endpoint returns {data_type}? Exact path and parameters.
4. RATE LIMITS: Requests per second/minute? Weight system? IP vs API-key limits?
5. PAGINATION: How does the API paginate historical data? (cursor, offset, timestamp-based?)
6. MAX RECORDS: Maximum records per request? Maximum date range per request?
7. RESPONSE FORMAT: Exact JSON structure of a successful response (field names, types, units).
8. TIMESTAMP FORMAT: Unix ms, Unix s, ISO 8601? What timezone?
9. ERROR CODES: Common error responses and their meaning.
10. KNOWN QUIRKS: Maintenance windows, data gaps, delayed data, deprecated endpoints.

Provide the actual endpoint URL and a sample request/response if possible.
Cite the official documentation URL."
```

Document findings in `src/data/api_specs/{source_name}.md`:
```markdown
# {Source Name} API Specification

## Base URL
{url}

## Authentication
{method and example}

## Endpoints Used
### {Endpoint 1}
- Path: {path}
- Method: GET
- Parameters: {list with types and constraints}
- Rate limit: {N requests per M seconds, weight: W}
- Max records per request: {N}
- Pagination: {method}

## Response Format
```json
{actual sample response}
```

## Rate Limit Strategy
{how to stay within limits for the target data volume}

## Known Issues
{maintenance windows, data gaps, deprecations}
```

### Step 3: Feasibility Assessment
Before implementation, verify:
- Can the API provide the required date range? (some APIs limit historical depth)
- Can the rate limits support the target data volume within reasonable time?
- Is authentication set up? (API keys in `.env`)
- Are there costs? (some endpoints are paid or tiered)

If infeasible, propose alternatives to the user.

### Step 4: Design Data Schema
Using the **data-engineer** subagent, design based on actual API response format:
- Map API response fields to internal OHLCV schema
- Define type conversions (API timestamp format → UTC datetime)
- Define additional fields available from the API
- Metadata schema (source, instrument, timeframe, fetch date, API version)

### Step 5: Implementation

**Assess scope**: Count the independent modules required.

| Scope | Action |
|-------|--------|
| Single data source, simple pipeline | Implement directly (Steps 5a-5c below) |
| Multiple data sources, or complex processing | **Transition to `/team-implement`** |

**If transitioning to `/team-implement`**, pass the schema design from Step 4:
```
Module assignments:
- data-engineer → src/data/fetcher_{source}.py (per data source)
- data-engineer → src/data/cleaner.py (normalization, quality checks)
- data-engineer → src/data/storage.py (Parquet write, dedup, metadata)
Interface contracts: {schema from Step 4, shared types}
```

**If implementing directly:**

#### Step 5a: Implement Fetcher
Create data fetching module in `src/data/`:
- API client matching the researched specification exactly
- Rate limiter matching the documented limits (not guessed)
- Pagination matching the API's actual pagination method
- Retry logic with backoff for documented error codes
- Request logging for debugging

#### Step 5b: Implement Cleaner
Create data cleaning module:
- Timezone normalization to UTC (from the API's documented format)
- Missing value detection and handling
- Outlier detection (price spikes, volume anomalies)
- OHLCV consistency checks (high >= max(open, close) >= low)
- Gap detection (missing candles vs market closures)

#### Step 5c: Storage
- Save to Parquet format in `data/` directory
- Generate metadata JSON alongside each data file
- Implement deduplication for re-fetches
- Store raw API responses for debugging (optional, configurable)

### Step 8: Validation
- Run data quality checks
- Verify row counts match expected candle count (trading days/hours * candles per period)
- Compare sample data against exchange UI or alternative source
- Test rate limiting (verify no 429 errors in a full fetch)
- Test pagination boundary (verify no duplicates or gaps at page boundaries)
- Test error recovery (simulate network failure mid-fetch)
