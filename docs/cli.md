# CLI Reference

Install: `pip install korea-real-estate`

All commands accept `--output <file.csv>` to save results as CSV.

---

## Commands

### `sales`
Land sale transactions for one calendar month.

```bash
korea-realestate sales --region 42820 --month 202501
korea-realestate sales --region 42820 --month 202501 --output sales.csv
```

### `commercial-sales`
Commercial, warehouse, and factory property sales for one month.

```bash
korea-realestate commercial-sales --region 42820 --month 202501
```

### `permits`
Building permit records for a region and date range.

```bash
korea-realestate permits --region 42820 --from 20240101 --to 20241231
```

### `zoning`
Zoning and land-use classifications for a region.

```bash
korea-realestate zoning --region 42820
korea-realestate zoning --region 42820 --dong 대진리
```

### `appraised-value`
Government-appraised individual land prices.

```bash
korea-realestate appraised-value --region 42820
korea-realestate appraised-value --region 42820 --year 2024
```

### `standard-price`
Publicly announced standard land prices.

```bash
korea-realestate standard-price --region 42820 --year 2024
```

### `building-ledger`
Building registry ledger (건축물대장) for a parcel.

```bash
korea-realestate building-ledger --region 42820
korea-realestate building-ledger --region 42820 --parcel 100-5
```

### `price-index`
REB real estate price index — land or housing.

```bash
korea-realestate price-index --region 42820 --type land --from 202401 --to 202412
korea-realestate price-index --region 42820 --type housing --from 202401 --to 202412
```

### `address-lookup`
Resolve a Korean address string to structured road/jibun fields.

```bash
korea-realestate address-lookup "강원도 고성군 대진리 123"
```

---

## Options

| Option | Commands | Description |
|---|---|---|
| `--region` | all except `address-lookup` | 5-digit 시군구 code (default: 42820) |
| `--month` | `sales`, `commercial-sales` | Year-month `YYYYMM` |
| `--from` / `--to` | `permits`, `price-index` | Date range `YYYYMMDD` or `YYYYMM` |
| `--year` | `appraised-value`, `standard-price` | Year integer |
| `--dong` | `zoning` | Dong name filter |
| `--parcel` | `building-ledger` | Jibun parcel e.g. `100-5` |
| `--type` | `price-index` | `land` or `housing` |
| `--output` | all | Save results to CSV file |
