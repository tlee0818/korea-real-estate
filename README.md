# korea-real-estate

**한국 공공 부동산 데이터 Python 클라이언트**

Thin Python HTTP client for Korean government real estate and property APIs. Returns raw parsed dicts — no transformation, no models.

[![CI](https://github.com/tlee0818/korea-real-estate/actions/workflows/ci.yml/badge.svg)](https://github.com/tlee0818/korea-real-estate/actions/workflows/ci.yml)
[![Lint](https://github.com/tlee0818/korea-real-estate/actions/workflows/lint.yml/badge.svg)](https://github.com/tlee0818/korea-real-estate/actions/workflows/lint.yml)
[![PyPI](https://img.shields.io/pypi/v/korea-real-estate)](https://pypi.org/project/korea-real-estate/)
[![Python](https://img.shields.io/pypi/pyversions/korea-real-estate)](https://pypi.org/project/korea-real-estate/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## What It Is

This client wraps Korea's public real estate APIs into a single Python interface. It covers:

- **Land & building transactions** — sale and lease prices by region and month
- **Permits & zoning** — building permits, land-use classifications, zoning records
- **Appraised & standard prices** — government-assessed and publicly announced land values
- **REITs** — company listings, investment targets, fundraising, AMC records
- **Onbid / KAMCO auctions** — property listings, bid results, regional statistics
- **Government property** — national asset sales/lease, relocation property, reserve inventory
- **Transit** — most-used transit routes by city
- **Address resolution** — Korean road/jibun address lookup (도로명주소)
- **Price index** — REB real estate price index (한국부동산원)
- **Regional datasets** — municipal-level broker registries, tax records, land/permit records

All methods return the raw API response as a Python dict (XML responses are parsed via `xmltodict`).

---

## Installation

```bash
pip install korea-real-estate
```

Python 3.11+ required.

---

## API Keys

You need **one key per data source**, not per endpoint.

| Source | Env Var | What It Covers |
|---|---|---|
| [data.go.kr](https://www.data.go.kr) | `PUBLIC_DATA_API_KEY` | Land/building/commercial transactions, permits, zoning, prices, REITs, Onbid, KAMCO, regional data |
| [NSDI](https://www.data.go.kr/data/15057159/openapi.do) | `NSDI_API_KEY` | Individual appraised land price |
| [REB (한국부동산원)](https://www.reb.or.kr/r-one/statistics/statisticsOpenapi.do) | `REB_API_KEY` | Real estate price index |
| [Juso (도로명주소)](https://business.juso.go.kr/addrlink/openApi/apiExprn.do) | `JUSO_API_KEY` | Address resolution |

To get a `data.go.kr` key: create an account, search for an API, click **활용신청**, then find your key under **마이페이지 → 오픈API 활용현황**. The key covers all `data.go.kr` endpoints.

`.env`:
```dotenv
PUBLIC_DATA_API_KEY=your_key_here
NSDI_API_KEY=your_key_here
REB_API_KEY=your_key_here
JUSO_API_KEY=your_key_here
```

---

## Quick Start

```python
from korea_realestate import KoreaRealEstateClient

client = KoreaRealEstateClient()

# Land sale transactions for one region and month
data = client.public_data.land_trade_history(region_code="42820", year_month="202501")

# Navigate the raw response
items = data["response"]["body"]["items"]["item"]

# Apartment lease records
data = client.public_data.apartment_rent_history(region_code="11230", year_month="202501")

# Address lookup
data = client.juso.address_lookup(keyword="강원도 고성군 대진리 123")
results = data["results"]["juso"]

# Real estate price index
data = client.reb.real_estate_price_index(
    region_code="42820",
    index_type="land",
    start_year_month="202401",
    end_year_month="202412",
)
```

---

## Client Structure

```
KoreaRealEstateClient
├── .public_data   PublicDataClient   ~67 methods — apis.data.go.kr
├── .reb           RebClient          1 method   — reb.or.kr price index
└── .juso          JusoClient         1 method   — juso.go.kr address API
```

See [docs/](docs/) for the full method reference.

---

## Error Handling

```python
from korea_realestate.exceptions import (
    APIKeyError,             # invalid, expired, or missing key
    RateLimitError,          # daily call limit exceeded
    InvalidParameterError,   # bad parameter value
    MissingParameterError,   # required parameter absent
    NoDataFoundError,        # no records for region/period
    ServerSideError,         # API server-side error
    NetworkError,            # connection timeout or unreachable host
    APIResponseError,        # unexpected HTTP or parse error
)
```

All exceptions inherit from `KoreaRealEstateError`. See [docs/errors.md](docs/errors.md).

---

## CLI

```bash
korea-realestate sales          --region 42820 --month 202501
korea-realestate commercial-sales --region 42820 --month 202501
korea-realestate permits        --region 42820 --from 20240101 --to 20241231
korea-realestate zoning         --region 42820
korea-realestate appraised-value --region 42820 --year 2024
korea-realestate standard-price  --region 42820 --year 2024
korea-realestate building-ledger --region 42820 --parcel 100-5
korea-realestate price-index    --region 42820 --type land --from 202401 --to 202412
korea-realestate address-lookup "강원도 고성군 대진리 123"
```

All commands support `--output <file.csv>`. See [docs/cli.md](docs/cli.md).

---

## Injection for Testing

```python
from unittest.mock import MagicMock
from korea_realestate import KoreaRealEstateClient
from korea_realestate.http import PublicDataClient, RebClient, JusoClient

client = KoreaRealEstateClient(
    public_data_client=MagicMock(spec=PublicDataClient),
    reb_client=MagicMock(spec=RebClient),
    juso_client=MagicMock(spec=JusoClient),
)
```

---

## Docs

- [Public Data API methods](docs/public_data.md)
- [REB price index](docs/reb.md)
- [Juso address API](docs/juso.md)
- [Error types](docs/errors.md)
- [CLI reference](docs/cli.md)

---

## License

MIT — see [LICENSE](LICENSE)
