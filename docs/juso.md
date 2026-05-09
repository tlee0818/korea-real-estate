# JusoClient — Method Reference

Methods on `client.juso`. Requires `JUSO_API_KEY` from [juso.go.kr](https://business.juso.go.kr/addrlink/openApi/apiExprn.do).

---

## `address_lookup(keyword, count_per_page=10, current_page=1)`

도로명주소 API — resolve a Korean address string to structured road and jibun fields.

**Parameters**

| Name | Type | Description |
|---|---|---|
| `keyword` | `str` | Address search string (Korean) |
| `count_per_page` | `int` | Results per page (default 10) |
| `current_page` | `int` | Page number (default 1) |

**Response shape**

```python
data["results"]["juso"]        # list of address records
data["results"]["common"]["totalCount"]  # total matches
```

Each address record includes: `roadAddr`, `jibunAddr`, `zipNo`, `admCd`, `rnMgtSn`, `bdMgtSn`, and more.

**Example**

```python
data = client.juso.address_lookup(keyword="강원도 고성군 대진리 123")
results = data["results"]["juso"]
for addr in results:
    print(addr["roadAddr"], addr["zipNo"])
```
