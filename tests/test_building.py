"""Tests for BuildingClient."""

from unittest.mock import MagicMock
import respx
import httpx
import pandas as pd

from korea_realestate.clients.building import BuildingClient
from korea_realestate.clients.events import EventsClient

from .conftest import FAKE_REGION, REGISTRY_XML

_REGISTRY_URL = "https://apis.data.go.kr/1613000/ArchPmsService/getApBdInfo"
_MAP_URL = "https://apis.data.go.kr/1613000/NSYDPnbldService/getNSYDPnbld"
_PERMITS_URL = "https://apis.data.go.kr/1613000/ArchPmsService/getApBasisOulnInfo"


@respx.mock
def test_get_registry_columns():
    respx.get(_REGISTRY_URL).mock(return_value=httpx.Response(200, text=REGISTRY_XML))
    client = BuildingClient()
    df = client.get_registry(region_code=FAKE_REGION)

    assert not df.empty
    assert set(["address", "building_name", "main_use", "structure",
                "floors_above", "total_area_sqm"]).issubset(df.columns)


@respx.mock
def test_get_registry_parses_row():
    respx.get(_REGISTRY_URL).mock(return_value=httpx.Response(200, text=REGISTRY_XML))
    client = BuildingClient()
    df = client.get_registry(region_code=FAKE_REGION)

    row = df.iloc[0]
    assert "대진리" in row["address"]
    assert row["main_use"] == "단독주택"
    assert row["floors_above"] == 2
    assert row["total_area_sqm"] == 150.0


@respx.mock
def test_get_map_layer_returns_geojson():
    respx.get(_MAP_URL).mock(return_value=httpx.Response(200, text=REGISTRY_XML))
    client = BuildingClient()
    result = client.get_map_layer(region_code=FAKE_REGION)

    assert result["type"] == "FeatureCollection"
    assert isinstance(result["features"], list)


def test_get_permit_history_delegates_to_events():
    mock_events = MagicMock(spec=EventsClient)
    mock_events.get_permit_history.return_value = pd.DataFrame({"permit_date": ["20240301"]})

    client = BuildingClient(events=mock_events)
    df = client.get_permit_history(
        region_code=FAKE_REGION, start_date="20240101", end_date="20241231", limit=3
    )

    mock_events.get_permit_history.assert_called_once_with(
        region_code=FAKE_REGION,
        start_date="20240101",
        end_date="20241231",
        permit_type=None,
        limit=3,
    )
    assert not df.empty


def test_get_full_profile_no_nearby():
    mock_events = MagicMock(spec=EventsClient)
    mock_events.get_permit_history.return_value = pd.DataFrame()

    client = BuildingClient(events=mock_events)

    with respx.mock:
        respx.get(_REGISTRY_URL).mock(return_value=httpx.Response(200, text=REGISTRY_XML))
        respx.get(_MAP_URL).mock(return_value=httpx.Response(200, text=REGISTRY_XML))

        profile = client.get_full_profile(region_code=FAKE_REGION, nearby_radius_m=None)

    assert profile["nearby"] is None
    assert "registry" in profile["building"]
    assert "map_layer" in profile["building"]
    assert "permits" in profile["history"]


def test_get_full_profile_nearby_returns_list():
    mock_events = MagicMock(spec=EventsClient)
    mock_events.get_permit_history.return_value = pd.DataFrame()

    client = BuildingClient(events=mock_events)

    with respx.mock:
        respx.get(_REGISTRY_URL).mock(return_value=httpx.Response(200, text=REGISTRY_XML))
        respx.get(_MAP_URL).mock(return_value=httpx.Response(200, text=REGISTRY_XML))

        profile = client.get_full_profile(region_code=FAKE_REGION, nearby_radius_m=500)

    assert isinstance(profile["nearby"], list)


def test_get_full_profile_history_limit():
    mock_events = MagicMock(spec=EventsClient)
    mock_events.get_permit_history.return_value = pd.DataFrame()

    client = BuildingClient(events=mock_events)

    with respx.mock:
        respx.get(_REGISTRY_URL).mock(return_value=httpx.Response(200, text=REGISTRY_XML))
        respx.get(_MAP_URL).mock(return_value=httpx.Response(200, text=REGISTRY_XML))

        client.get_full_profile(region_code=FAKE_REGION, history_limit=3)

    call_kwargs = mock_events.get_permit_history.call_args[1]
    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    expected_start = (datetime.now() - relativedelta(months=3)).strftime("%Y%m%d")
    assert call_kwargs["start_date"] == expected_start
