# korea-real-estate

**한국 공공 부동산 데이터 Python 클라이언트**

Thin Python HTTP client for Korean government real estate APIs. Returns raw parsed dicts — no transformation, no models.

[![CI](https://github.com/tlee0818/korea-real-estate/actions/workflows/ci.yml/badge.svg)](https://github.com/tlee0818/korea-real-estate/actions/workflows/ci.yml)
[![Lint](https://github.com/tlee0818/korea-real-estate/actions/workflows/lint.yml/badge.svg)](https://github.com/tlee0818/korea-real-estate/actions/workflows/lint.yml)
[![PyPI](https://img.shields.io/pypi/v/korea-real-estate)](https://pypi.org/project/korea-real-estate/)
[![Python](https://img.shields.io/pypi/pyversions/korea-real-estate)](https://pypi.org/project/korea-real-estate/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Installation

```bash
pip install korea-real-estate
```

Python 3.11+ required.

---

## API Keys

**You need one key per data source, not per endpoint.**

| Source | Env Var | Covers |
|---|---|---|
| [data.go.kr](https://www.data.go.kr) | `PUBLIC_DATA_API_KEY` | Land sales, commercial sales, permits, zoning, standard price, building ledger, building footprints |
| [NSDI](https://www.data.go.kr/data/15057159/openapi.do) | `NSDI_API_KEY` | Individual appraised land price |
| [REB (한국부동산원)](https://www.reb.or.kr/r-one/statistics/statisticsOpenapi.do) | `REB_API_KEY` | Real estate price index |
| [Juso (도로명주소)](https://business.juso.go.kr/addrlink/openApi/apiExprn.do) | `JUSO_API_KEY` | Address resolution |

### Getting keys

**data.go.kr** (covers 7 of the 9 endpoints):
1. Create account at [data.go.kr](https://www.data.go.kr)
2. Search for each API, click **활용신청** (Apply for use)
3. Your single service key is in **마이페이지 → 오픈API 활용현황**

> Keys from data.go.kr are URL-encoded. Use as-is — do **not** re-encode.

**REB, NSDI, Juso** each have their own portals linked above.

---

## Configuration

```bash
cp .env.example .env
```

`.env`:

```dotenv
PUBLIC_DATA_API_KEY=your_key_here   # data.go.kr — covers all public data endpoints
NSDI_API_KEY=your_key_here          # individual appraised land price
REB_API_KEY=your_key_here           # real estate price index
JUSO_API_KEY=your_key_here          # address resolution

DEFAULT_REGION_CODE=42820
REQUEST_TIMEOUT_SECONDS=30
MAX_RETRIES=3
```

---

## Quick Start

```python
from korea_realestate import KoreaRealEstateClient

client = KoreaRealEstateClient()

# Land sales — raw dict straight from the API
data = client.public_data.land_trade_history(region_code="42820", year_month="202501")

# Navigate the response
items = data["response"]["body"]["items"]["item"]
```

---

## Client Structure

```
KoreaRealEstateClient
├── .public_data   PublicDataClient   apis.data.go.kr
├── .reb           RebClient          reb.or.kr
└── .juso          JusoClient         juso.go.kr
```

All methods return the raw parsed dict from the API (XML → dict via xmltodict, JSON → dict natively).

---

## `client.public_data` — PublicDataClient

All endpoints use your single `PUBLIC_DATA_API_KEY`, except `individual_land_price` which uses `NSDI_API_KEY`.

```python
# Land sale transactions — one calendar month
data = client.public_data.land_trade_history(
    region_code="42820",
    year_month="202501",       # YYYYMM
    num_rows=1000,
)

# Commercial / warehouse / factory sales — one calendar month
data = client.public_data.commercial_trade_history(
    region_code="42820",
    year_month="202501",
    num_rows=1000,
)

# Building permit records
data = client.public_data.building_permit_records(
    region_code="42820",
    start_date="20240101",     # YYYYMMDD, optional
    end_date="20241231",       # YYYYMMDD, optional
    num_rows=1000,
)

# Zoning and land-use classification
data = client.public_data.land_use_zoning(
    region_code="42820",
    dong="대진리",             # subdivision filter, optional
    num_rows=1000,
)

# Government-appraised individual land price (NSDI — uses NSDI_API_KEY)
data = client.public_data.individual_land_price(
    region_code="42820",
    year=2024,                 # optional
    num_rows=1000,
)

# Publicly announced standard land price
data = client.public_data.standard_land_price(
    region_code="42820",
    year=2024,
    num_rows=1000,
)

# Building ledger (건축물대장)
data = client.public_data.building_ledger(
    region_code="42820",
    parcel_main="100",         # optional
    parcel_sub="5",            # optional
    ledger_type="표제부",      # 표제부 | 총괄표제부 | 층별개요 | 지역지구구역
    num_rows=1000,
)

# Building footprints (GIS)
data = client.public_data.building_spatial_info(
    region_code="42820",
    bbox=(127.0, 37.0, 128.0, 38.0),  # (minX, minY, maxX, maxY), optional
    num_rows=1000,
)
```

---

## `client.reb` — RebClient

```python
# Real estate price index — land or housing (한국부동산원)
data = client.reb.real_estate_price_index(
    region_code="42820",
    index_type="land",         # "land" or "housing"
    start_year_month="202401", # YYYYMM, optional
    end_year_month="202412",   # YYYYMM, optional
    num_rows=500,
)
```

---

## `client.juso` — JusoClient

```python
# Resolve a Korean address string
data = client.juso.address_lookup(
    keyword="강원도 고성군 대진리 123",
    count_per_page=10,
    current_page=1,
)

# Results are under data["results"]["juso"]
results = data["results"]["juso"]
```

---

## Error Handling

```python
from korea_realestate.exceptions import (
    APIKeyError,          # missing, invalid, or expired key
    RateLimitError,       # daily call limit exceeded
    RegionNotFoundError,  # no data for region/period
    APIResponseError,     # unexpected HTTP or XML error
)

try:
    data = client.public_data.land_trade_history(region_code="42820", year_month="202501")
except APIKeyError as e:
    print("Check your API key:", e)
except RateLimitError:
    print("Daily limit exceeded — try again tomorrow")
```

---

## Injection for Testing

```python
from unittest.mock import MagicMock
from korea_realestate.http import PublicDataClient, RebClient, JusoClient

client = KoreaRealEstateClient(
    public_data_client=MagicMock(spec=PublicDataClient),
    reb_client=MagicMock(spec=RebClient),
    juso_client=MagicMock(spec=JusoClient),
)
```

---

## CLI

```bash
korea-realestate sales          --region 42820 --month 202501
korea-realestate commercial-sales --region 42820 --month 202501
korea-realestate permits        --region 42820 --from 20240101 --to 20241231
korea-realestate zoning         --region 42820 --dong 대진리
korea-realestate appraised-value --region 42820 --year 2024
korea-realestate standard-price  --region 42820 --year 2024
korea-realestate building-ledger --region 42820 --parcel 100-5
korea-realestate price-index    --region 42820 --type land --from 202401 --to 202412
korea-realestate address-lookup "강원도 고성군 대진리 123"
```

All commands accept `--output <file.csv>`.

---

## Running Tests

```bash
pip install "korea-real-estate[dev]"
pytest
```

Tests use `respx` to mock HTTP — no real API keys needed.

---

## Region Codes

5-digit 시군구 codes (법정동코드 앞 5자리).

| Region | Code | Region | Code |
|---|---|---|---|
| 고성군 (강원) | 42820 | 속초시 | 42210 |
| 양양군 | 42830 | 인제군 | 42810 |
| 춘천시 | 42110 | 원주시 | 42130 |
| 강릉시 | 42150 | 동해시 | 42170 |
| 강남구 | 11230 | 서초구 | 11220 |
| 송파구 | 11240 | 용산구 | 11030 |
| 수원시영통구 | 41117 | 성남시분당구 | 41135 |
| 제주시 | 50110 | 서귀포시 | 50130 |
| 세종시 | 36110 | 해운대구 | 21090 |

```python
from korea_realestate.utils import get_code

get_code("고성군")  # → "42820"
get_code("고성")    # → "42820" (fuzzy match)
```

---

## License

MIT — see [LICENSE](LICENSE)
