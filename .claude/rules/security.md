# Security Rules

## API Key Management

### Mandatory Rules
- API keys MUST be loaded via **environment variables** (`.env` file + python-dotenv)
- Hardcoding keys in source code is **strictly prohibited**
- `.env` file MUST be in `.gitignore`
- Separate test and production keys

### Recommended .env Structure
```
# .env (gitignored)
BINANCE_API_KEY=xxx
BINANCE_SECRET_KEY=xxx
BYBIT_API_KEY=xxx
BYBIT_SECRET_KEY=xxx
MT5_LOGIN=xxx
MT5_PASSWORD=xxx
MT5_SERVER=xxx
```

## Exchange API Security

- **IP restriction**: Set IP whitelist on API keys (recommended)
- **Least privilege**: Grant only necessary permissions (read-only, trade, withdrawal separated)
- **No withdrawal permission**: Automated trading API keys MUST NOT have withdrawal rights
- **Rate limiting**: Implement logic to respect API rate limits

## Wallet / Address Management

- Hardcoding wallet addresses is **prohibited**
- Deposit/withdrawal addresses via config files only
- Implement address verification mechanism on change

## Test Environment

- **Testnet mandatory**: Always verify on testnet before production deployment
  - Binance Testnet
  - bybit Testnet
  - MT5 Demo account
- NEVER mix test and production API keys

## Code Security

- No sensitive information in log output
- No API keys/secrets in error messages
- Implement HTTP request signature verification
- Never disable SSL/TLS certificate verification
