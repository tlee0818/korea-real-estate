"""Tests for KoreaRealEstateClient (master client)."""

from unittest.mock import MagicMock

from korea_realestate.client import KoreaRealEstateClient
from korea_realestate.http.juso import JusoClient
from korea_realestate.http.public_data import PublicDataClient
from korea_realestate.http.reb import RebClient


def test_instantiates_without_error():
    client = KoreaRealEstateClient()
    assert client is not None


def test_all_namespaces_accessible():
    client = KoreaRealEstateClient()
    assert isinstance(client.public_data, PublicDataClient)
    assert isinstance(client.reb, RebClient)
    assert isinstance(client.juso, JusoClient)


def test_injectable_mock_public_data_client():
    mock = MagicMock(spec=PublicDataClient)
    client = KoreaRealEstateClient(public_data_client=mock)
    assert client.public_data is mock


def test_injectable_mock_reb_client():
    mock = MagicMock(spec=RebClient)
    client = KoreaRealEstateClient(reb_client=mock)
    assert client.reb is mock


def test_injectable_mock_juso_client():
    mock = MagicMock(spec=JusoClient)
    client = KoreaRealEstateClient(juso_client=mock)
    assert client.juso is mock
