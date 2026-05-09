# RebClient — Method Reference

Methods on `client.reb`. Requires `REB_API_KEY` from [reb.or.kr](https://www.reb.or.kr/r-one/statistics/statisticsOpenapi.do).

---

## `real_estate_price_index(region_code, index_type, start_year_month=None, end_year_month=None, num_rows=500)`

부동산 가격지수 — real estate price index from 한국부동산원 (Korea Real Estate Board).

**Parameters**

| Name | Type | Description |
|---|---|---|
| `region_code` | `str` | 5-digit 시군구 code |
| `index_type` | `str` | `"land"` or `"housing"` |
| `start_year_month` | `str \| None` | Start period `YYYYMM` |
| `end_year_month` | `str \| None` | End period `YYYYMM` |
| `num_rows` | `int` | Max rows (default 500) |

**Example**

```python
data = client.reb.real_estate_price_index(
    region_code="42820",
    index_type="land",
    start_year_month="202401",
    end_year_month="202412",
)
```
