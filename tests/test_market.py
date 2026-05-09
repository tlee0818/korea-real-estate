"""Tests for MarketClient."""

from unittest.mock import MagicMock
import pytest
import respx
import httpx
import pandas as pd

from korea_realestate.clients.market import MarketClient
from korea_realestate.clients.events import EventsClient

from .conftest import FAKE_REGION, TRENDS_XML

_TRENDS_URL = "https://www.reb.or.kr/r-one/openapi/SttsApiTblData.do"
_COMMERCIAL_URL = "https://apis.data.go.kr/1613000/RTMSDataSvcNrgTrade/getRTMSDataSvcNrgTrade"


@respx.mock
def test_get_price_trends_columns():
    respx.get(_TRENDS_URL).mock(return_value=httpx.Response(200, text=TRENDS_XML))
    client = MarketClient()
    df = client.get_price_trends(
        region_code=FAKE_REGION, index_type="land",
        start_year_month="202403", end_year_month="202403"
    )

    assert not df.empty
    assert set(["period", "region", "index_value", "change_pct_mom", "change_pct_yoy"]).issubset(df.columns)


@respx.mock
def test_get_price_trends_parses_row():
    respx.get(_TRENDS_URL).mock(return_value=httpx.Response(200, text=TRENDS_XML))
    client = MarketClient()
    df = client.get_price_trends(
        region_code=FAKE_REGION, index_type="land",
        start_year_month="202403", end_year_month="202403"
    )

    row = df.iloc[0]
    assert row["period"] == "202403"
    assert float(row["index_value"]) == pytest.approx(101.5, rel=1e-3)


@respx.mock
def test_get_price_trends_invalid_type():
    client = MarketClient()
    with pytest.raises(ValueError, match="index_type"):
        client.get_price_trends(region_code=FAKE_REGION, index_type="invalid")


@respx.mock
def test_get_price_trends_limit():
    respx.get(_TRENDS_URL).mock(return_value=httpx.Response(200, text=TRENDS_XML))
    client = MarketClient()
    df = client.get_price_trends(
        region_code=FAKE_REGION, index_type="land",
        start_year_month="202403", end_year_month="202403",
        limit=1,
    )
    assert len(df) <= 1


def test_get_commercial_comps_delegates_to_events():
    mock_events = MagicMock(spec=EventsClient)
    mock_events.get_commercial_sales.return_value = pd.DataFrame({"deal_date": ["2024-03-15"]})

    client = MarketClient(events=mock_events)
    df = client.get_commercial_comps(
        region_code=FAKE_REGION, start_year_month="202403", end_year_month="202403", limit=5
    )

    mock_events.get_commercial_sales.assert_called_once_with(
        region_code=FAKE_REGION,
        start_year_month="202403",
        end_year_month="202403",
        property_type=None,
        limit=5,
    )
    assert not df.empty


def test_get_full_profile_no_nearby():
    mock_events = MagicMock(spec=EventsClient)
    mock_events.get_commercial_sales.return_value = pd.DataFrame()

    client = MarketClient(events=mock_events)

    with respx.mock:
        respx.get(_TRENDS_URL).mock(return_value=httpx.Response(200, text=TRENDS_XML))
        profile = client.get_full_profile(region_code=FAKE_REGION, nearby_radius_m=None)

    assert profile["nearby"] is None
    assert "land" in profile["trends"]
    assert "housing" in profile["trends"]
    assert "commercial_sales" in profile["history"]


def test_get_full_profile_nearby_returns_list():
    mock_events = MagicMock(spec=EventsClient)
    mock_events.get_commercial_sales.return_value = pd.DataFrame()

    client = MarketClient(events=mock_events)

    with respx.mock:
        respx.get(_TRENDS_URL).mock(return_value=httpx.Response(200, text=TRENDS_XML))
        profile = client.get_full_profile(region_code=FAKE_REGION, nearby_radius_m=500)

    assert isinstance(profile["nearby"], list)


def test_get_full_profile_history_limit():
    mock_events = MagicMock(spec=EventsClient)
    mock_events.get_commercial_sales.return_value = pd.DataFrame()

    client = MarketClient(events=mock_events)

    with respx.mock:
        respx.get(_TRENDS_URL).mock(return_value=httpx.Response(200, text=TRENDS_XML))
        client.get_full_profile(region_code=FAKE_REGION, history_limit=3)

    call_kwargs = mock_events.get_commercial_sales.call_args[1]
    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    expected_start = (datetime.now() - relativedelta(months=3)).strftime("%Y%m")
    assert call_kwargs["start_year_month"] == expected_start
