# korea-real-estate

**한국 공공 부동산 데이터 Python 클라이언트**

Python library and CLI for querying Korean government real estate data: land sales, building permits, price trend indices, appraised values, zoning, and address resolution.

[![CI](https://github.com/tlee0818/korea-real-estate/actions/workflows/ci.yml/badge.svg)](https://github.com/tlee0818/korea-real-estate/actions/workflows/ci.yml)
[![Lint](https://github.com/tlee0818/korea-real-estate/actions/workflows/lint.yml/badge.svg)](https://github.com/tlee0818/korea-real-estate/actions/workflows/lint.yml)
[![PyPI](https://img.shields.io/pypi/v/korea-real-estate)](https://pypi.org/project/korea-real-estate/)
[![Python](https://img.shields.io/pypi/pyversions/korea-real-estate)](https://pypi.org/project/korea-real-estate/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Contents

- [Installation](#installation)
- [Getting API Keys](#getting-api-keys)
- [Configuration](#configuration)
- [Quick Start](#quick-start)
- [Client Reference](#client-reference)
  - [KoreaRealEstateClient (master)](#korearealestateclient-master)
  - [EventsClient — historical transactions](#eventsclient--historical-transactions)
  - [LandClient — parcel data](#landclient--parcel-data)
  - [BuildingClient — building registry](#buildingclient--building-registry)
  - [MarketClient — price trends](#marketclient--price-trends)
  - [AddressClient — address resolution](#addressclient--address-resolution)
- [Error Handling](#error-handling)
- [CLI Reference](#cli-reference)
- [Region Codes](#region-codes)
- [API Reference Links](#api-reference-links)

---

## Installation

```bash
pip install korea-real-estate
```

Python 3.11+ required.

---

## Getting API Keys

Each data source requires a separate key from the Korean government data portal.

1. Create an account at [www.data.go.kr](https://www.data.go.kr)
2. Search for each API and click **활용신청** (Apply for use)
3. Copy your **서비스키** from **마이페이지 → 오픈API 활용현황**

| Env Var | API | Portal Link |
|---|---|---|
| `SALES_HISTORY_API_KEY` | 토지 매매 실거래가 | [15126466](https://www.data.go.kr/data/15126466/openapi.do) |
| `COMMERCIAL_SALES_API_KEY` | 상업용 부동산 매매 실거래가 | [15058017](https://www.data.go.kr/data/15058017/openapi.do) |
| `BUILDING_PERMITS_API_KEY` | 건축인허가 정보 | [15044525](https://www.data.go.kr/data/15044525/openapi.do) |
| `ZONING_API_KEY` | 토지이용계획 | [15113034](https://www.data.go.kr/data/15113034/openapi.do) |
| `APPRAISED_VALUE_API_KEY` | 개별공시지가 (NSDI) | [15057159](https://www.data.go.kr/data/15057159/openapi.do) |
| `STANDARD_LAND_PRICE_API_KEY` | 표준지공시지가 | [15056649](https://www.data.go.kr/data/15056649/openapi.do) |
| `BUILDING_REGISTRY_API_KEY` | 건축물대장 | [15044521](https://www.data.go.kr/data/15044521/openapi.do) |
| `BUILDING_MAP_API_KEY` | 건물 공간정보 | [15058453](https://www.data.go.kr/data/15058453/openapi.do) |
| `PRICE_TRENDS_API_KEY` | 한국부동산원 통계 (REB) | [reb.or.kr](https://www.reb.or.kr/r-one/statistics/statisticsOpenapi.do) |
| `ADDRESS_RESOLVER_API_KEY` | 주소 검색 (Juso) | [juso.go.kr](https://business.juso.go.kr/addrlink/openApi/apiExprn.do) |

> Keys from data.go.kr are URL-encoded. Use them as-is — do **not** re-encode.

---

## Configuration

```bash
cp .env.example .env
```

`.env`:

```dotenv
# Historical transactions
SALES_HISTORY_API_KEY=your_key_here
COMMERCIAL_SALES_API_KEY=your_key_here
BUILDING_PERMITS_API_KEY=your_key_here

# Land parcel
ZONING_API_KEY=your_key_here
APPRAISED_VALUE_API_KEY=your_key_here
STANDARD_LAND_PRICE_API_KEY=your_key_here

# Building
BUILDING_REGISTRY_API_KEY=your_key_here
BUILDING_MAP_API_KEY=your_key_here

# Market trends (REB)
PRICE_TRENDS_API_KEY=your_key_here

# Address resolution (Juso)
ADDRESS_RESOLVER_API_KEY=your_key_here

# Defaults
DEFAULT_REGION_CODE=42820
REQUEST_TIMEOUT_SECONDS=30
MAX_RETRIES=3
```

Never commit `.env` — it is git-ignored.

---

## Quick Start

```python
from korea_realestate import KoreaRealEstateClient

client = KoreaRealEstateClient()

# Land sales last 6 months
df = client.events.get_land_sales(region_code="42820", start_year_month="202410", end_year_month="202503")

# Official appraised land value
df = client.land.get_appraised_value(region_code="42820", year=2024)

# Building registry
df = client.building.get_registry(region_code="42820")

# Market price trend
df = client.market.get_price_trends(region_code="42820", index_type="land", start_year_month="202401", end_year_month="202412")

# Resolve address
result = client.address.resolve("강원도 고성군 대진리 123")
```

---

## Client Reference

### KoreaRealEstateClient (master)

Single entry point. Instantiates and wires all domain clients with shared HTTP connections.

```python
from korea_realestate import KoreaRealEstateClient

client = KoreaRealEstateClient()

client.events    # EventsClient
client.land      # LandClient
client.building  # BuildingClient
client.market    # MarketClient
client.address   # AddressClient
```

For testing, inject mock HTTP clients:

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

### EventsClient — historical transactions

```python
# Land sales
df = client.events.get_land_sales(
    region_code="42820",
    start_year_month="202401",
    end_year_month="202412",
    land_category="임",   # optional: 임 | 전 | 답 | 대 | …
    limit=50,             # most recent N rows
)
# columns: deal_date, region, dong, parcel, land_category, area_sqm,
#          price_10k_won, price_per_sqm, zoning, buyer_type, cancelled

# Commercial / factory / warehouse sales
df = client.events.get_commercial_sales(
    region_code="42820",
    start_year_month="202401",
    end_year_month="202412",
    property_type="상업용",  # optional
    limit=20,
)
# columns: deal_date, region, dong, building_use, land_area_sqm,
#          building_area_sqm, floors, build_year, price_10k_won

# Building permits
df = client.events.get_permit_history(
    region_code="42820",
    start_date="20240101",
    end_date="20241231",
    permit_type="신축",   # optional: 신축 | 증축 | 대수선 | 철거
    limit=10,
)
# columns: address, permit_type, main_use, site_area_sqm, building_area_sqm,
#          floor_area_ratio, coverage_ratio, permit_date, start_date, completion_date
```

---

### LandClient — parcel data

```python
# Zoning classification
df = client.land.get_zoning(region_code="42820", dong="대진리")
# columns: region, dong, parcel, land_category, zoning_class, area_sqm

# Official appraised land value (개별공시지가)
df = client.land.get_appraised_value(region_code="42820", year=2024)
# columns: region, dong, parcel, area_sqm, value_per_sqm, total_value, reference_year

# Standard land price (표준지공시지가)
df = client.land.get_standard_price(region_code="42820", year=2024)
# columns: region, dong, parcel, land_category, area_sqm, price_per_sqm,
#          reference_year, zoning, terrain, road_access

# Full parcel profile (all sources combined)
profile = client.land.get_full_profile(
    region_code="42820",
    history_limit=12,       # months of sales history
    nearby_radius_m=500,    # optional: include nearby parcels snapshot
)
# profile["parcel"]["zoning"]          → DataFrame
# profile["parcel"]["appraised_value"] → DataFrame
# profile["parcel"]["standard_price"]  → DataFrame
# profile["history"]["sales"]          → DataFrame
# profile["nearby"]                    → list | None
```

---

### BuildingClient — building registry

```python
# Building registry (건축물대장)
df = client.building.get_registry(
    region_code="42820",
    parcel_main="100",   # optional
    parcel_sub="5",      # optional
    ledger_type="표제부",  # 표제부 | 총괄표제부 | 층별개요 | 지역지구구역
)
# columns: address, building_name, main_use, structure,
#          floors_above, total_area_sqm, …

# Building map layer (GeoJSON)
geojson = client.building.get_map_layer(region_code="42820")
# geojson["type"] == "FeatureCollection"

# Permit history (delegates to EventsClient)
df = client.building.get_permit_history(
    region_code="42820",
    start_date="20240101",
    end_date="20241231",
)

# Full building profile
profile = client.building.get_full_profile(
    region_code="42820",
    history_limit=12,
    nearby_radius_m=None,
)
# profile["building"]["registry"]   → DataFrame
# profile["building"]["map_layer"]  → GeoJSON dict
# profile["history"]["permits"]     → DataFrame
# profile["nearby"]                 → list | None
```

---

### MarketClient — price trends

```python
# Land or housing price index (한국부동산원)
df = client.market.get_price_trends(
    region_code="42820",
    index_type="land",          # "land" or "housing"
    start_year_month="202401",
    end_year_month="202412",
    limit=12,
)
# columns: period, region, index_value, change_pct_mom, change_pct_yoy

# Commercial property comparables (delegates to EventsClient)
df = client.market.get_commercial_comps(
    region_code="42820",
    start_year_month="202401",
    end_year_month="202412",
)

# Full market profile
profile = client.market.get_full_profile(region_code="42820", history_limit=12)
# profile["trends"]["land"]              → DataFrame
# profile["trends"]["housing"]           → DataFrame
# profile["history"]["commercial_sales"] → DataFrame
```

---

### AddressClient — address resolution

```python
# Resolve one address
result = client.address.resolve("강원도 고성군 대진리 123")
# result: {road_addr, jibun_addr, zip, region_code, x, y, …}

# Batch resolve
results = client.address.resolve_many(["주소1", "주소2"])

# Get 5-digit 시군구 region code from address string
code = client.address.to_region_code("고성군 대진리")  # → "42820"
```

---

## Error Handling

```python
from korea_realestate.exceptions import (
    APIKeyError,          # missing, invalid, or expired key
    RateLimitError,       # daily call limit exceeded
    RegionNotFoundError,  # no data returned for region/period
    APIResponseError,     # unexpected HTTP or XML error
)

try:
    df = client.events.get_land_sales(region_code="42820", start_year_month="202401", end_year_month="202412")
except APIKeyError as e:
    print("Check your API key:", e)
except RateLimitError:
    print("Daily limit exceeded — try again tomorrow")
except RegionNotFoundError:
    print("No data for this region/period")
except APIResponseError as e:
    print("Unexpected API error:", e)
```

---

## CLI Reference

Keys are read from `.env` automatically.

```bash
# Land sales
korea-realestate sales --region 42820 --from 202401 --to 202412 --land-category 임 --output sales.csv

# Commercial / factory / warehouse sales
korea-realestate commercial-sales --region 42820 --from 202401 --to 202412

# Building permits
korea-realestate permits --region 42820 --from 20240101 --to 20241231 --type 신축

# Zoning lookup
korea-realestate zoning --region 42820 --dong 대진리

# Official appraised land value
korea-realestate appraised-value --region 42820 --year 2024

# Price trend index
korea-realestate price-trends --region 42820 --type land --from 202401 --to 202412

# Building registry
korea-realestate building-registry --region 42820 --parcel 100-5

# Resolve address
korea-realestate resolve-address "강원도 고성군 대진리 123"
```

All commands accept `--output <file.csv>` to save results.

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

Lookup helper:

```python
from korea_realestate.utils import get_code

code = get_code("고성군")  # → "42820"
code = get_code("고성")    # → "42820" (fuzzy match)
```

---

## API Reference Links

| API | Portal |
|---|---|
| Land Sales | [data.go.kr/15126466](https://www.data.go.kr/data/15126466/openapi.do) |
| Commercial Sales | [data.go.kr/15058017](https://www.data.go.kr/data/15058017/openapi.do) |
| Building Permits | [data.go.kr/15044525](https://www.data.go.kr/data/15044525/openapi.do) |
| Zoning | [data.go.kr/15113034](https://www.data.go.kr/data/15113034/openapi.do) |
| Appraised Value | [data.go.kr/15057159](https://www.data.go.kr/data/15057159/openapi.do) |
| Standard Land Price | [data.go.kr/15056649](https://www.data.go.kr/data/15056649/openapi.do) |
| Building Registry | [data.go.kr/15044521](https://www.data.go.kr/data/15044521/openapi.do) |
| Building Map | [data.go.kr/15058453](https://www.data.go.kr/data/15058453/openapi.do) |
| Price Trends (REB) | [reb.or.kr](https://www.reb.or.kr/r-one/statistics/statisticsOpenapi.do) |
| Address (Juso) | [juso.go.kr](https://business.juso.go.kr/addrlink/openApi/apiExprn.do) |

---

## License

MIT — see [LICENSE](LICENSE)
