"""Tests for EventsClient."""

import pytest
import respx
import httpx

from korea_realestate.clients.events import EventsClient

from .conftest import (
    FAKE_REGION,
    SALES_XML,
    COMMERCIAL_XML,
    PERMIT_XML,
    RATE_LIMIT_XML,
    INVALID_KEY_XML,
    EMPTY_XML,
)

from korea_realestate.exceptions import RateLimitError, APIKeyError

_LAND_SALES_URL = "https://apis.data.go.kr/1613000/RTMSDataSvcLandTrade/getRTMSDataSvcLandTrade"
_COMMERCIAL_URL = "https://apis.data.go.kr/1613000/RTMSDataSvcNrgTrade/getRTMSDataSvcNrgTrade"
_PERMITS_URL = "https://apis.data.go.kr/1613000/ArchPmsService/getApBasisOulnInfo"


@respx.mock
def test_get_land_sales_returns_correct_columns():
    respx.get(_LAND_SALES_URL).mock(return_value=httpx.Response(200, text=SALES_XML))
    client = EventsClient()
    df = client.get_land_sales(region_code=FAKE_REGION, start_year_month="202403", end_year_month="202403")

    assert not df.empty
    assert set(["deal_date", "region", "dong", "land_category", "area_sqm",
                "price_10k_won", "price_per_sqm", "zoning", "buyer_type", "cancelled"]).issubset(df.columns)


@respx.mock
def test_get_land_sales_parses_row():
    respx.get(_LAND_SALES_URL).mock(return_value=httpx.Response(200, text=SALES_XML))
    client = EventsClient()
    df = client.get_land_sales(region_code=FAKE_REGION, start_year_month="202403", end_year_month="202403")

    row = df.iloc[0]
    assert row["dong"] == "대진리"
    assert row["land_category"] == "임"
    assert row["area_sqm"] == 500.0
    assert row["price_10k_won"] == 5000
    assert row["price_per_sqm"] == pytest.approx(10.0, rel=1e-3)


@respx.mock
def test_get_land_sales_limit():
    respx.get(_LAND_SALES_URL).mock(return_value=httpx.Response(200, text=SALES_XML))
    client = EventsClient()
    df = client.get_land_sales(region_code=FAKE_REGION, start_year_month="202403", end_year_month="202403", limit=1)
    assert len(df) <= 1


@respx.mock
def test_get_land_sales_empty_region():
    respx.get(_LAND_SALES_URL).mock(return_value=httpx.Response(200, text=EMPTY_XML))
    client = EventsClient()
    df = client.get_land_sales(region_code=FAKE_REGION, start_year_month="202403", end_year_month="202403")
    assert df.empty


@respx.mock
def test_get_land_sales_date_range_calls_per_month():
    calls = []

    def side_effect(request):
        calls.append(request)
        return httpx.Response(200, text=SALES_XML)

    respx.get(_LAND_SALES_URL).mock(side_effect=side_effect)
    client = EventsClient()
    df = client.get_land_sales(region_code=FAKE_REGION, start_year_month="202401", end_year_month="202403")
    assert len(calls) == 3  # one per month
    assert len(df) == 3


@respx.mock
def test_get_land_sales_rate_limit_raises():
    respx.get(_LAND_SALES_URL).mock(return_value=httpx.Response(200, text=RATE_LIMIT_XML))
    client = EventsClient()
    with pytest.raises(RateLimitError):
        client.get_land_sales(region_code=FAKE_REGION, start_year_month="202403", end_year_month="202403")


@respx.mock
def test_get_land_sales_invalid_key_raises():
    respx.get(_LAND_SALES_URL).mock(return_value=httpx.Response(200, text=INVALID_KEY_XML))
    client = EventsClient()
    with pytest.raises(APIKeyError):
        client.get_land_sales(region_code=FAKE_REGION, start_year_month="202403", end_year_month="202403")


def test_get_land_sales_requires_date_range():
    client = EventsClient()
    with pytest.raises(ValueError, match="start_year_month"):
        client.get_land_sales(region_code=FAKE_REGION)


@respx.mock
def test_get_commercial_sales_returns_correct_columns():
    respx.get(_COMMERCIAL_URL).mock(return_value=httpx.Response(200, text=COMMERCIAL_XML))
    client = EventsClient()
    df = client.get_commercial_sales(region_code=FAKE_REGION, start_year_month="202403", end_year_month="202403")

    assert not df.empty
    assert set(["deal_date", "region", "dong", "building_use",
                "land_area_sqm", "building_area_sqm", "price_10k_won"]).issubset(df.columns)


@respx.mock
def test_get_commercial_sales_limit():
    respx.get(_COMMERCIAL_URL).mock(return_value=httpx.Response(200, text=COMMERCIAL_XML))
    client = EventsClient()
    df = client.get_commercial_sales(
        region_code=FAKE_REGION, start_year_month="202403", end_year_month="202403", limit=1
    )
    assert len(df) <= 1


@respx.mock
def test_get_permit_history_returns_correct_columns():
    respx.get(_PERMITS_URL).mock(return_value=httpx.Response(200, text=PERMIT_XML))
    client = EventsClient()
    df = client.get_permit_history(region_code=FAKE_REGION)

    assert not df.empty
    assert set(["address", "permit_type", "main_use", "land_area_sqm",
                "building_area_sqm", "permit_date"]).issubset(df.columns)


@respx.mock
def test_get_permit_history_limit():
    respx.get(_PERMITS_URL).mock(return_value=httpx.Response(200, text=PERMIT_XML))
    client = EventsClient()
    df = client.get_permit_history(region_code=FAKE_REGION, limit=1)
    assert len(df) <= 1


@respx.mock
def test_get_permit_history_type_filter():
    respx.get(_PERMITS_URL).mock(return_value=httpx.Response(200, text=PERMIT_XML))
    client = EventsClient()
    df = client.get_permit_history(region_code=FAKE_REGION, permit_type="신축")
    assert not df.empty
    assert all(df["permit_type"].str.contains("신축", na=False))
