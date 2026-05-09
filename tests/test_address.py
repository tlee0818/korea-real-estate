"""Tests for AddressClient."""

import pytest
import respx
import httpx

from korea_realestate.clients.address import AddressClient

from .conftest import ADDRESS_JSON

_JUSO_URL = "https://business.juso.go.kr/addrlink/addrLinkApi.do"


@respx.mock
def test_resolve_returns_structured_dict():
    respx.get(_JUSO_URL).mock(return_value=httpx.Response(200, text=ADDRESS_JSON))
    client = AddressClient()
    result = client.resolve("강원도 고성군 대진리 123")

    assert result["sido"] == "강원특별자치도"
    assert result["sigungu"] == "고성군"
    assert result["eupmyeondong"] == "대진리"
    assert result["postal_code"] == "24763"
    assert result["sigungu_code"] == "42820"
    assert result["latitude"] == pytest.approx(38.58)
    assert result["longitude"] == pytest.approx(128.37)


@respx.mock
def test_resolve_road_and_parcel_address():
    respx.get(_JUSO_URL).mock(return_value=httpx.Response(200, text=ADDRESS_JSON))
    client = AddressClient()
    result = client.resolve("강원도 고성군 대진리 123")

    assert "고성군" in result["road_address"]
    assert "대진리" in result["parcel_address"]


@respx.mock
def test_resolve_many():
    respx.get(_JUSO_URL).mock(return_value=httpx.Response(200, text=ADDRESS_JSON))
    client = AddressClient()
    results = client.resolve_many(["주소1", "주소2"])

    assert len(results) == 2
    assert all("sigungu" in r for r in results)


@respx.mock
def test_to_region_code():
    respx.get(_JUSO_URL).mock(return_value=httpx.Response(200, text=ADDRESS_JSON))
    client = AddressClient()
    code = client.to_region_code("강원도 고성군")

    assert code == "42820"


def test_resolve_not_found():
    not_found_json = '{"results": {"common": {"totalCount": "0", "errorCode": "0"}, "juso": []}}'
    with respx.mock:
        respx.get(_JUSO_URL).mock(return_value=httpx.Response(200, text=not_found_json))
        client = AddressClient()
        with pytest.raises(ValueError, match="not found"):
            client.resolve("존재하지않는주소")
