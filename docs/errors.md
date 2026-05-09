# Error Handling

All exceptions inherit from `KoreaRealEstateError`. Import from `korea_realestate.exceptions`.

---

## Exception Hierarchy

```
KoreaRealEstateError
├── APIKeyError              — invalid, expired, or unauthorized API key
├── RateLimitError           — daily call limit exceeded (code 22)
├── NoDataFoundError         — no records found for given parameters (code 03/50)
├── ServerSideError          — server-side application/database error (code 01/02/500)
├── NetworkError             — connection failure, timeout, or malformed response
└── APIResponseError         — unexpected HTTP status or unparseable response
    ├── InvalidParameterError    — bad parameter value (code 10/51)
    └── MissingParameterError    — required parameter absent (code 11/52)
```

---

## When Each Is Raised

| Exception | Trigger |
|---|---|
| `APIKeyError` | Result code 30 (invalid key), 21 (temporarily unavailable), 33 (unsigned call) |
| `RateLimitError` | Result code 22 (daily limit exceeded) |
| `InvalidParameterError` | Result code 10 or 51 |
| `MissingParameterError` | Result code 11 or 52 |
| `NoDataFoundError` | Result code 03 or 50 — valid request, zero records |
| `ServerSideError` | Result code 01 (app error), 02 (DB error), 500 (internal error) |
| `NetworkError` | `httpx.ConnectError`, `httpx.TimeoutException`, `httpx.RemoteProtocolError`, or retries exhausted |
| `APIResponseError` | Non-retryable HTTP error status, or unrecognized result code |

---

## Example

```python
from korea_realestate.exceptions import (
    APIKeyError,
    RateLimitError,
    NoDataFoundError,
    NetworkError,
    KoreaRealEstateError,
)

try:
    data = client.public_data.land_trade_history(region_code="42820", year_month="202501")
except APIKeyError:
    print("Check PUBLIC_DATA_API_KEY")
except RateLimitError:
    print("Daily limit hit — retry tomorrow")
except NoDataFoundError:
    print("No transactions found for this region/month")
except NetworkError as e:
    print(f"Network problem: {e}")
except KoreaRealEstateError as e:
    print(f"API error: {e}")
```
