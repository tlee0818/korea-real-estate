# PublicDataClient — Method Reference

All methods on `client.public_data`. Requires `PUBLIC_DATA_API_KEY` (except `individual_land_price`, which uses `NSDI_API_KEY`).

All methods return a raw parsed dict. Typical response shape:

```python
data["response"]["body"]["items"]["item"]  # list of records
data["response"]["body"]["totalCount"]     # total available rows
```

---

## Land & Building

### `land_trade_history(region_code, year_month, num_rows=1000)`
토지 매매 실거래가 — land sale transactions for one calendar month.

### `commercial_trade_history(region_code, year_month, num_rows=1000)`
상업업무용·공장창고 매매 실거래가 — commercial, warehouse, and factory property sales for one month.

### `building_permit_records(region_code, start_date=None, end_date=None, num_rows=1000)`
건축인허가 기본개요 — building permit records for a region and optional date range (`YYYYMMDD`).

### `land_use_zoning(region_code, dong=None, num_rows=1000)`
토지이용계획 — zoning and land-use classifications for a region.

### `individual_land_price(region_code, year=None, num_rows=1000)`
개별공시지가 — government-appraised individual land prices (NSDI). Uses `NSDI_API_KEY`.

### `standard_land_price(region_code, year=None, num_rows=1000)`
표준지공시지가 — publicly announced standard land prices.

### `building_ledger(region_code, dong_code=None, parcel_main=None, parcel_sub=None, ledger_type="표제부", num_rows=1000)`
건축물대장 — building registry ledger for a parcel. `ledger_type` options: `표제부`, `총괄표제부`, `층별개요`, `지역지구구역`.

### `building_spatial_info(region_code, bbox=None, num_rows=1000)`
GIS 건물 도면 — building footprints. Pass `bbox=(minX, minY, maxX, maxY)` to clip to a bounding box.

---

## Apartment & Housing Transactions

All methods take `(region_code, year_month, num_rows=1000)`.

| Method | Description |
|---|---|
| `apartment_trade_history` | 아파트 매매 실거래가 — apartment sales |
| `apartment_trade_history_detailed` | 아파트 매매 실거래가 상세 — detailed apartment sales with floor/area |
| `apartment_rent_history` | 아파트 전월세 실거래가 — apartment lease/jeonse |
| `officetel_trade_history` | 오피스텔 매매 실거래가 — officetel sales |
| `officetel_rent_history` | 오피스텔 전월세 실거래가 — officetel lease/jeonse |
| `rowhouse_multiplex_trade_history` | 연립다세대 매매 실거래가 — rowhouse/multi-family sales |
| `rowhouse_multiplex_rent_history` | 연립다세대 전월세 실거래가 — rowhouse/multi-family leases |
| `detached_house_trade_history` | 단독/다가구 매매 실거래가 — detached house sales |
| `detached_house_rent_history` | 단독/다가구 전월세 실거래가 — detached house leases |
| `apartment_presale_rights_trade_history` | 아파트 분양권전매 실거래가 — pre-sale rights transfers |
| `industrial_warehouse_factory_trade_history` | 공장·창고 매매 실거래가 — industrial property sales |

---

## REITs

All methods take `(num_rows=100, page=1, **kwargs)`.

| Method | Description |
|---|---|
| `reits_company_list` | 부동산투자회사(리츠) 정보 — registered REITs companies |
| `reits_investment_targets` | 리츠 투자대상 목록 — assets held by REITs companies |
| `reits_announcements` | 리츠 공시 목록 — REITs regulatory disclosures |
| `reits_fundraising_list` | 리츠 모집·매출 목록 — REITs fundraising/share offerings |
| `reits_amc_company_list` | 자산관리회사(AMC) 정보 — registered AMC companies |
| `reits_amc_consignment_contracts` | AMC 업무수탁 목록 — AMC management contracts |
| `reits_amc_announcements` | AMC 공시 목록 — AMC regulatory disclosures |
| `reits_amc_fundraising_list` | AMC 모집·매출 목록 — AMC fundraising/share offerings |

---

## Onbid / KAMCO Public Auctions

### `onbid_property_detail(property_id, auction_condition_no=None, **kwargs)`
온비드 부동산 물건상세 조회 — detailed listing for one Onbid property by management number.

### `onbid_bid_result_detail(property_id=None, num_rows=100, page=1, **kwargs)`
온비드 물건 입찰결과상세 조회 — detailed bid results for a specific property.

Methods taking `(num_rows=100, page=1, **kwargs)`:

| Method | Description |
|---|---|
| `onbid_property_listing` | 온비드 부동산 물건목록 — active auction listings |
| `onbid_interest_rank` | 온비드 관심물건 순위 — properties ranked by bookmarks |
| `onbid_view_count_rank` | 온비드 조회수 순위 — properties ranked by page views |
| `onbid_high_markdown_rank` | 온비드 저감률 순위 — highest price reduction (50%+) properties |
| `onbid_announcement_property_info` | 온비드 공고상세 물건정보 — properties in an announcement |
| `onbid_announcement_bid_results` | 온비드 공고 입찰결과목록 — bid results for an announcement |
| `onbid_announcement_detail` | 온비드 공고상세 조회 — full auction announcement details |
| `onbid_kamco_regional_bid_stats` | KAMCO 지역별 입찰통계 — KAMCO bid stats by region |
| `onbid_org_regional_bid_stats` | 기관별 지역별 입찰통계 — org-level bid stats by region |
| `onbid_kamco_property_type_bid_stats` | KAMCO 용도별 입찰통계 — KAMCO bid stats by property type |
| `onbid_org_property_type_bid_stats` | 기관별 용도별 입찰통계 — org-level bid stats by property type |
| `onbid_property_bid_info` | 온비드 물건 입찰정보 — bid schedule and conditions |

---

## KAMCO Government Property

All methods take `(num_rows=100, page=1, **kwargs)`.

| Method | Description |
|---|---|
| `kamco_relocation_property_status` | 종전부동산 현황 — former residential properties for relocation programs |
| `kamco_reserve_property_inventory` | 비축부동산 명세 — reserve property inventory |
| `public_development_property_vacancy` | 공공개발부동산 공실정보 — vacancy info for publicly developed properties |
| `public_development_property_facilities` | 공공개발부동산 시설현황 — facility details for publicly developed properties |
| `kamco_interest_rate_schedule` | 부동산공통 이율관리 — KAMCO transaction interest rate schedules |
| `kamco_appraisal_agency_registry` | 부동산공통 감정기관정보 — certified appraisal agency registry |
| `national_property_sales_status` | 국유부동산 매각현황 — government-owned property sales status |
| `national_property_lease_status` | 국유부동산 임대현황 — government-owned property lease status |
| `seized_property_auction_win_rate` | 압류재산 공매 낙찰가율 — seized property auction win rates |
| `entrusted_nonbusiness_property_sales` | 수탁 비업무용 자산 매각정보 — non-business asset disposal sales |

---

## Transit

### `most_frequent_transit_routes(city, period="monthly", num_rows=1000)`
최빈교통이용 경로 데이터 — most frequently used transit OD pairs for a city.

- `city`: `seoul`, `incheon`, `gyeonggi`, `busan`, `daegu`, `gwangju`, `daejeon`, `ulsan`, `jeju`
- `period`: `"monthly"` or `"yearly"`

---

## Regional Government APIs

All methods take `(num_rows=1000, page=1, **kwargs)`.

| Method | Region | Description |
|---|---|---|
| `yeongcheon_real_estate_brokers` | 영천시 (경북) | Licensed real estate broker registry |
| `daegu_donggu_real_estate_brokers` | 대구 동구 | Licensed real estate broker registry |
| `daegu_donggu_mandatory_managed_apartments` | 대구 동구 | Apartments under mandatory management |
| `daegu_donggu_maintenance_project_status` | 대구 동구 | Urban redevelopment project status |
| `yeongdeok_individual_house_prices` | 영덕군 (경북) | Officially assessed individual house prices |
| `sangju_building_standard_values` | 상주시 (경북) | Standard assessed building values |
| `yeongju_land_property` | 영주시 (경북) | Land property records |
| `yeongju_use_district` | 영주시 (경북) | Land use district designations |
| `yeongju_development_permits` | 영주시 (경북) | Development activity permits |
| `yeongju_forest_land_conversion_permits` | 영주시 (경북) | Forest land conversion permits |
| `yeongju_farmland_conversion_permits` | 영주시 (경북) | Farmland conversion permits |
| `yeongju_local_tax_arrears` | 영주시 (경북) | Annual local tax arrears |

---

## Other National APIs

All methods take `(num_rows=100, page=1, **kwargs)`.

| Method | Description |
|---|---|
| `public_data_statistics_list` | 공동저장소 통계리스트 — available public dataset statistics |
| `issuance_tax_grant_by_year` | 연도별 교부세 — annual local government grant statistics (MOIS) |
| `bankruptcy_institution_real_estate_listings` | 파산금융회사 매물현황 — properties from bankrupt financial institutions (KDIC) |
