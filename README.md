# Korea Real Estate API — Python Client

**한국 공공 부동산 데이터 Python 클라이언트**

A Python library and CLI for querying Korean government real estate data: past land sales, price trend indices, official appraised values, and zoning classifications.

---

## Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Getting API Keys](#getting-api-keys)
- [Configuration](#configuration)
- [Python Client Usage](#python-client-usage)
- [CLI Reference](#cli-reference)
- [Region Codes](#region-codes)
- [API Reference Links](#api-reference-links)

---

## Prerequisites

- Python 3.11 or later
- API keys from [data.go.kr](https://www.data.go.kr)

---

## Installation

```bash
git clone https://github.com/your-org/korea-realestate-api.git
cd korea-realestate-api
pip install -r requirements.txt

# Or install as a package
pip install -e .
```

---

## Getting API Keys

Each API requires a separate key from the Korean government data portal.

1. Create an account at [www.data.go.kr](https://www.data.go.kr)
2. Search for each API by name (links below)
3. Click **활용신청** (Apply for use)
4. Wait for approval (usually instant for open APIs)
5. Copy your **서비스키** (service key) from **마이페이지 → 오픈API 활용현황**

| Client | API Name (Korean) | data.go.kr Link |
|---|---|---|
| `SalesHistoryClient` | 토지 매매 실거래가 | [15126466](https://www.data.go.kr/data/15126466/openapi.do) |
| `PriceTrendsClient` | 한국부동산원 통계 | [15134761](https://www.data.go.kr/data/15134761/openapi.do) |
| `AppraisedValueClient` | 개별공시지가 | [15057159](https://www.data.go.kr/data/15057159/openapi.do) |
| `ZoningClient` | 토지이용계획 | [15113034](https://www.data.go.kr/data/15113034/openapi.do) |

> **Note:** Keys are URL-encoded by data.go.kr. Use them as-is — do **not** re-encode them.

---

## Configuration

Copy the example env file and fill in your keys:

```bash
cp .env.example .env
```

Edit `.env`:

```dotenv
SALES_HISTORY_API_KEY=your_key_here
PRICE_TRENDS_API_KEY=your_key_here
APPRAISED_VALUE_API_KEY=your_key_here
ZONING_API_KEY=your_key_here

DEFAULT_REGION_CODE=42820   # 고성군 — change to your region
REQUEST_TIMEOUT_SECONDS=30
MAX_RETRIES=3
```

The `.env` file is git-ignored. Never commit your API keys.

---

## Python Client Usage

All clients require an explicit `api_key` argument. The `default_region` argument is optional and falls back to `DEFAULT_REGION_CODE` from `.env`.

### SalesHistoryClient — Past Land Sale Transactions

```python
import os
from korea_realestate.clients import SalesHistoryClient

client = SalesHistoryClient(
    api_key=os.environ["SALES_HISTORY_API_KEY"],
    default_region="42820",   # optional
)

# Single month
df = client.get_sales(region_code="42820", year_month="202501")

# Date range
df = client.get_sales(
    region_code="42820",
    start_year_month="202001",
    end_year_month="202501",
)

# Filter by land category
df = client.get_sales(
    region_code="42820",
    start_year_month="202001",
    end_year_month="202501",
    land_category="임",   # 임야 only; also accepts "forest"
)

print(df.columns.tolist())
# ['deal_date', 'region', 'dong', 'parcel', 'land_category',
#  'area_sqm', 'price_10k_won', 'price_per_sqm', 'zoning',
#  'buyer_type', 'cancelled']
```

### PriceTrendsClient — Market Price Trend Indices

```python
import os
from korea_realestate.clients import PriceTrendsClient

client = PriceTrendsClient(api_key=os.environ["PRICE_TRENDS_API_KEY"])

# Land price change index (지가변동률)
df = client.get_trend_index(
    index_type="land",
    region_code="42820",
    start_year_month="202001",
    end_year_month="202501",
)

# Housing price trend (주택가격동향)
df = client.get_trend_index(
    index_type="housing",
    region_code="42820",
    start_year_month="202001",
    end_year_month="202501",
)

print(df.columns.tolist())
# ['period', 'region', 'index_value', 'change_pct_mom', 'change_pct_yoy']
```

### AppraisedValueClient — Government Appraised Land Value

```python
import os
from korea_realestate.clients import AppraisedValueClient

client = AppraisedValueClient(api_key=os.environ["APPRAISED_VALUE_API_KEY"])

df = client.get_appraised_value(region_code="42820", year=2024)

print(df.columns.tolist())
# ['region', 'dong', 'parcel', 'area_sqm', 'value_per_sqm',
#  'total_value', 'reference_year']
```

### ZoningClient — Zoning & Land Use Classification

```python
import os
from korea_realestate.clients import ZoningClient

client = ZoningClient(api_key=os.environ["ZONING_API_KEY"])

# All parcels in region
df = client.get_zoning(region_code="42820")

# Filter to a specific 동
df = client.get_zoning(region_code="42820", dong="대진리")

print(df.columns.tolist())
# ['region', 'dong', 'parcel', 'land_category', 'zoning_class',
#  'zoning_detail', 'area_sqm', 'restrictions']
```

### Error Handling

```python
from korea_realestate.exceptions import (
    APIKeyError,        # missing/invalid/expired key
    RateLimitError,     # daily call limit exceeded
    RegionNotFoundError,# no data for the region
    APIResponseError,   # unexpected HTTP or XML error
)

try:
    df = client.get_sales(region_code="42820", year_month="202501")
except APIKeyError as e:
    print("Check your API key:", e)
except RateLimitError:
    print("Daily limit exceeded — try again tomorrow")
except RegionNotFoundError:
    print("No data for this region/period")
```

---

## CLI Reference

```bash
# Past land sales
python -m korea_realestate sales \
  --region 42820 \
  --from 2020-01 \
  --to 2025-01 \
  --land-category 임 \
  --output sales.csv

# Zoning lookup
python -m korea_realestate zoning \
  --region 42820 \
  --dong 대진리

# Price trend index
python -m korea_realestate price-trends \
  --region 42820 \
  --type land \
  --from 2020-01 \
  --to 2025-01

# Government appraised value
python -m korea_realestate appraised-value \
  --region 42820 \
  --year 2024
```

API keys are read from `.env` automatically. You can also pass them inline:

```bash
python -m korea_realestate sales --api-key YOUR_KEY --region 42820 --from 2024-01 --to 2024-12
```

---

## Region Codes

5-digit 시군구 codes (법정동코드 앞 5자리). Pass as `--region` or `region_code=`.

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

For the full list, see [korea_realestate/utils/region_codes.py](korea_realestate/utils/region_codes.py) or use the lookup helper:

```python
from korea_realestate.utils import get_code, REGION_CODES

code = get_code("고성군")   # → "42820"
code = get_code("고성")     # → "42820" (fuzzy match)
```

---

## Running Tests

```bash
pip install -r requirements.txt
pytest tests/ -v
```

Tests use `respx` to mock HTTP calls — no real API keys needed.

---

## API Reference Links

| API | data.go.kr Page |
|---|---|
| Land Sales History | https://www.data.go.kr/data/15126466/openapi.do |
| Market Price Trends | https://www.data.go.kr/data/15134761/openapi.do |
| Appraised Land Value | https://www.data.go.kr/data/15057159/openapi.do |
| Zoning & Land Use | https://www.data.go.kr/data/15113034/openapi.do |

---

## License

MIT
