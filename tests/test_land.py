"""Tests for LandClient."""

from unittest.mock import MagicMock
import respx
import httpx

from korea_realestate.clients.land import LandClient
from korea_realestate.clients.events import EventsClient

from .conftest import (
    FAKE_REGION,
    SALES_XML,
    ZONING_XML,
    APPRAISED_XML,
    STANDARD_PRICE_XML,
)

_LAND_SALES_URL = "https://apis.data.go.kr/1613000/RTMSDataSvcLandTrade/getRTMSDataSvcLandTrade"
_ZONING_URL = "https://apis.data.go.kr/1613000/LandUseService/getLandUseList"
_APPRAISED_URL = "https://apis.data.go.kr/1611000/nsdi/IndvdLandPriceService/wfs/IndvdLandPrice"
_STANDARD_URL = "https://apis.data.go.kr/1613000/PubLandPriceService/getPblcLandPriceList"


@respx.mock
def test_get_zoning_columns():
    respx.get(_ZONING_URL).mock(return_value=httpx.Response(200, text=ZONING_XML))
    client = LandClient()
    df = client.get_zoning(region_code=FAKE_REGION)

    assert not df.empty
    assert set(["region", "dong", "parcel", "land_category", "zoning_class", "area_sqm"]).issubset(df.columns)


@respx.mock
def test_get_zoning_parses_row():
    respx.get(_ZONING_URL).mock(return_value=httpx.Response(200, text=ZONING_XML))
    client = LandClient()
    df = client.get_zoning(region_code=FAKE_REGION)

    row = df.iloc[0]
    assert row["dong"] == "대진리"
    assert row["land_category"] == "임"
    assert row["zoning_class"] == "계획관리지역"


@respx.mock
def test_get_appraised_value_columns():
    respx.get(_APPRAISED_URL).mock(return_value=httpx.Response(200, text=APPRAISED_XML))
    client = LandClient()
    df = client.get_appraised_value(region_code=FAKE_REGION, year=2024)

    assert not df.empty
    assert set(["region", "dong", "parcel", "area_sqm", "value_per_sqm", "total_value", "reference_year"]).issubset(df.columns)


@respx.mock
def test_get_appraised_value_total_computed():
    respx.get(_APPRAISED_URL).mock(return_value=httpx.Response(200, text=APPRAISED_XML))
    client = LandClient()
    df = client.get_appraised_value(region_code=FAKE_REGION, year=2024)

    row = df.iloc[0]
    assert row["value_per_sqm"] == 50000
    assert row["total_value"] == 50000 * 500


@respx.mock
def test_get_standard_price_columns():
    respx.get(_STANDARD_URL).mock(return_value=httpx.Response(200, text=STANDARD_PRICE_XML))
    client = LandClient()
    df = client.get_standard_price(region_code=FAKE_REGION, year=2024)

    assert not df.empty
    assert set(["region", "dong", "parcel", "land_category", "area_sqm",
                "price_per_sqm", "reference_year", "zoning", "terrain", "road_access"]).issubset(df.columns)


@respx.mock
def test_get_sales_history_delegates_to_events():
    respx.get(_LAND_SALES_URL).mock(return_value=httpx.Response(200, text=SALES_XML))
    mock_events = MagicMock(spec=EventsClient)
    mock_events.get_land_sales.return_value = __import__("pandas").DataFrame({"deal_date": ["2024-03-15"]})

    client = LandClient(events=mock_events)
    df = client.get_sales_history(
        region_code=FAKE_REGION, start_year_month="202403", end_year_month="202403", limit=5
    )

    mock_events.get_land_sales.assert_called_once_with(
        region_code=FAKE_REGION,
        start_year_month="202403",
        end_year_month="202403",
        land_category=None,
        limit=5,
    )
    assert not df.empty


@respx.mock
def test_get_full_profile_no_nearby(monkeypatch):
    respx.get(_ZONING_URL).mock(return_value=httpx.Response(200, text=ZONING_XML))
    respx.get(_APPRAISED_URL).mock(return_value=httpx.Response(200, text=APPRAISED_XML))
    respx.get(_STANDARD_URL).mock(return_value=httpx.Response(200, text=STANDARD_PRICE_XML))
    respx.get(_LAND_SALES_URL).mock(return_value=httpx.Response(200, text=SALES_XML))

    client = LandClient()
    profile = client.get_full_profile(region_code=FAKE_REGION, nearby_radius_m=None)

    assert profile["nearby"] is None
    assert "zoning" in profile["parcel"]
    assert "appraised_value" in profile["parcel"]
    assert "standard_price" in profile["parcel"]
    assert "sales" in profile["history"]


def test_get_full_profile_nearby_radius_returns_list():
    mock_events = MagicMock(spec=EventsClient)
    import pandas as pd
    mock_events.get_land_sales.return_value = pd.DataFrame()

    client = LandClient(events=mock_events)

    with respx.mock:
        respx.get(_ZONING_URL).mock(return_value=httpx.Response(200, text=ZONING_XML))
        respx.get(_APPRAISED_URL).mock(return_value=httpx.Response(200, text=APPRAISED_XML))
        respx.get(_STANDARD_URL).mock(return_value=httpx.Response(200, text=STANDARD_PRICE_XML))

        profile = client.get_full_profile(region_code=FAKE_REGION, nearby_radius_m=500)

    # nearby is a list (not None), even if empty — confirms nearby logic was invoked
    assert isinstance(profile["nearby"], list)


def test_get_full_profile_history_limit_passes_correct_range():
    mock_events = MagicMock(spec=EventsClient)
    import pandas as pd
    mock_events.get_land_sales.return_value = pd.DataFrame()

    client = LandClient(events=mock_events)

    with respx.mock:
        respx.get(_ZONING_URL).mock(return_value=httpx.Response(200, text=ZONING_XML))
        respx.get(_APPRAISED_URL).mock(return_value=httpx.Response(200, text=APPRAISED_XML))
        respx.get(_STANDARD_URL).mock(return_value=httpx.Response(200, text=STANDARD_PRICE_XML))

        client.get_full_profile(region_code=FAKE_REGION, history_limit=3)

    call_kwargs = mock_events.get_land_sales.call_args[1]
    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    expected_start = (datetime.now() - relativedelta(months=3)).strftime("%Y%m")
    assert call_kwargs["start_year_month"] == expected_start
