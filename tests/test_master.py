"""Tests for KoreaRealEstateClient (master client)."""

from unittest.mock import MagicMock

from korea_realestate.clients.master import KoreaRealEstateClient
from korea_realestate.clients.events import EventsClient
from korea_realestate.clients.land import LandClient
from korea_realestate.clients.building import BuildingClient
from korea_realestate.clients.market import MarketClient
from korea_realestate.clients.address import AddressClient
from korea_realestate.http.public_data import PublicDataClient
from korea_realestate.http.reb import RebClient
from korea_realestate.http.juso import JusoClient


def test_instantiates_without_error():
    client = KoreaRealEstateClient()
    assert client is not None


def test_all_namespaces_accessible():
    client = KoreaRealEstateClient()
    assert isinstance(client.land, LandClient)
    assert isinstance(client.building, BuildingClient)
    assert isinstance(client.market, MarketClient)
    assert isinstance(client.events, EventsClient)
    assert isinstance(client.address, AddressClient)


def test_events_instance_shared_with_land():
    client = KoreaRealEstateClient()
    assert client.land._events is client.events


def test_events_instance_shared_with_building():
    client = KoreaRealEstateClient()
    assert client.building._events is client.events


def test_events_instance_shared_with_market():
    client = KoreaRealEstateClient()
    assert client.market._events is client.events


def test_address_instance_shared_with_land():
    client = KoreaRealEstateClient()
    assert client.land._address is client.address


def test_address_instance_shared_with_building():
    client = KoreaRealEstateClient()
    assert client.building._address is client.address


def test_public_data_http_shared_across_domains():
    client = KoreaRealEstateClient()
    assert client.land._http is client.building._http
    assert client.land._http is client.events._http


def test_reb_http_used_by_market():
    client = KoreaRealEstateClient()
    assert client.market._http is client._http.reb


def test_injectable_mock_public_data_client():
    mock_public = MagicMock(spec=PublicDataClient)
    client = KoreaRealEstateClient(public_data_client=mock_public)

    # Mock flows all the way down
    assert client.land._http is mock_public
    assert client.building._http is mock_public
    assert client.events._http is mock_public


def test_injectable_mock_reb_client():
    mock_reb = MagicMock(spec=RebClient)
    client = KoreaRealEstateClient(reb_client=mock_reb)
    assert client.market._http is mock_reb


def test_injectable_mock_juso_client():
    mock_juso = MagicMock(spec=JusoClient)
    client = KoreaRealEstateClient(juso_client=mock_juso)
    assert client.address._http is mock_juso


def test_standalone_land_client_works():
    land = LandClient()
    assert land is not None
    assert land._events is not None
    assert land._address is not None


def test_standalone_building_client_works():
    building = BuildingClient()
    assert building is not None


def test_standalone_market_client_works():
    market = MarketClient()
    assert market is not None


def test_standalone_events_client_works():
    events = EventsClient()
    assert events is not None


def test_standalone_address_client_works():
    address = AddressClient()
    assert address is not None
