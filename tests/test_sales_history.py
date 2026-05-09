import pytest
import respx
import httpx

from korea_realestate.clients import SalesHistoryClient
from korea_realestate.exceptions import APIKeyError, RateLimitError

from .conftest import FAKE_KEY, FAKE_REGION, SALES_XML, RATE_LIMIT_XML, INVALID_KEY_XML

_ENDPOINT = "https://apis.data.go.kr/1613000/RTMSDataSvcLandTrade/getRTMSDataSvcLandTrade"


def test_requires_api_key():
    with pytest.raises(APIKeyError, match="api_key"):
        SalesHistoryClient(api_key="")


def test_requires_api_key_none():
    with pytest.raises(TypeError):
        SalesHistoryClient()


@respx.mock
def test_get_sales_single_month():
    respx.get(_ENDPOINT).mock(return_value=httpx.Response(200, text=SALES_XML))

    client = SalesHistoryClient(api_key=FAKE_KEY, default_region=FAKE_REGION)
    df = client.get_sales(region_code=FAKE_REGION, year_month="202403")

    assert len(df) == 1
    assert df.iloc[0]["dong"] == "대진리"
    assert df.iloc[0]["land_category"] == "임"
    assert df.iloc[0]["area_sqm"] == 500.0
    assert df.iloc[0]["price_10k_won"] == 5000


@respx.mock
def test_get_sales_price_per_sqm_computed():
    respx.get(_ENDPOINT).mock(return_value=httpx.Response(200, text=SALES_XML))

    client = SalesHistoryClient(api_key=FAKE_KEY)
    df = client.get_sales(region_code=FAKE_REGION, year_month="202403")

    assert df.iloc[0]["price_per_sqm"] == pytest.approx(10.0, rel=1e-3)


@respx.mock
def test_get_sales_date_range(monkeypatch):
    call_count = 0

    def mock_get(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        return httpx.Response(200, text=SALES_XML)

    respx.get(_ENDPOINT).mock(side_effect=mock_get)

    client = SalesHistoryClient(api_key=FAKE_KEY)
    df = client.get_sales(
        region_code=FAKE_REGION,
        start_year_month="202401",
        end_year_month="202403",
    )
    assert len(df) == 3  # one row per month × 3 months


@respx.mock
def test_rate_limit_raises():
    respx.get(_ENDPOINT).mock(return_value=httpx.Response(200, text=RATE_LIMIT_XML))

    client = SalesHistoryClient(api_key=FAKE_KEY)
    with pytest.raises(RateLimitError):
        client.get_sales(region_code=FAKE_REGION, year_month="202403")


@respx.mock
def test_invalid_key_raises():
    respx.get(_ENDPOINT).mock(return_value=httpx.Response(200, text=INVALID_KEY_XML))

    client = SalesHistoryClient(api_key=FAKE_KEY)
    with pytest.raises(APIKeyError):
        client.get_sales(region_code=FAKE_REGION, year_month="202403")


def test_land_category_filter():
    import pandas as pd
    from korea_realestate.clients.sales_history import _items_to_df

    items = [
        {"dealYear": "2024", "dealMonth": "3", "dealDay": "1",
         "siGunGu": "고성군", "umdNm": "대진리", "jibun": "1",
         "landCdNm": "임", "area": "100", "dealAmount": "500",
         "landUse": "계획관리", "buyerGbn": "개인", "cdealType": ""},
        {"dealYear": "2024", "dealMonth": "3", "dealDay": "2",
         "siGunGu": "고성군", "umdNm": "대진리", "jibun": "2",
         "landCdNm": "전", "area": "200", "dealAmount": "1000",
         "landUse": "농업진흥", "buyerGbn": "법인", "cdealType": ""},
    ]
    df = _items_to_df(items)
    filtered = df[df["land_category"].str.contains("임", na=False)]
    assert len(filtered) == 1
    assert filtered.iloc[0]["land_category"] == "임"
