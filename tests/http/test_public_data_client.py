"""Tests for PublicDataClient — named endpoint methods, retry, parse, error logic."""

import pytest
import respx
import httpx

from korea_realestate.http.public_data import PublicDataClient
from korea_realestate.exceptions import APIKeyError, RateLimitError, APIResponseError

from tests.conftest import (
    SALES_XML, COMMERCIAL_XML, PERMIT_XML,
    ZONING_XML, APPRAISED_XML, STANDARD_PRICE_XML,
    REGISTRY_XML, RATE_LIMIT_XML, INVALID_KEY_XML,
)

_LAND_SALES_URL     = "https://apis.data.go.kr/1613000/RTMSDataSvcLandTrade/getRTMSDataSvcLandTrade"
_COMMERCIAL_URL     = "https://apis.data.go.kr/1613000/RTMSDataSvcNrgTrade/getRTMSDataSvcNrgTrade"
_PERMIT_URL         = "https://apis.data.go.kr/1613000/ArchPmsService/getApBasisOulnInfo"
_ZONING_URL         = "https://apis.data.go.kr/1613000/LandUseService/getLandUseList"
_APPRAISED_URL      = "https://apis.data.go.kr/1611000/nsdi/IndvdLandPriceService/wfs/IndvdLandPrice"
_STANDARD_URL       = "https://apis.data.go.kr/1613000/PubLandPriceService/getPblcLandPriceList"
_REGISTRY_URL       = "https://apis.data.go.kr/1613000/ArchPmsService/getApBdInfo"
_MAP_URL            = "https://apis.data.go.kr/1613000/NSYDPnbldService/getNSYDPnbld"


@respx.mock
def test_get_land_sales_hits_correct_endpoint():
    route = respx.get(_LAND_SALES_URL).mock(return_value=httpx.Response(200, text=SALES_XML))
    PublicDataClient().get_land_sales(region_code="42820", year_month="202403")
    assert route.called


@respx.mock
def test_get_land_sales_injects_service_key():
    route = respx.get(_LAND_SALES_URL).mock(return_value=httpx.Response(200, text=SALES_XML))
    PublicDataClient().get_land_sales(region_code="42820", year_month="202403")
    assert "serviceKey" in dict(route.calls[0].request.url.params)


@respx.mock
def test_get_commercial_sales_hits_correct_endpoint():
    route = respx.get(_COMMERCIAL_URL).mock(return_value=httpx.Response(200, text=COMMERCIAL_XML))
    PublicDataClient().get_commercial_sales(region_code="42820", year_month="202403")
    assert route.called


@respx.mock
def test_get_permit_history_hits_correct_endpoint():
    route = respx.get(_PERMIT_URL).mock(return_value=httpx.Response(200, text=PERMIT_XML))
    PublicDataClient().get_permit_history(region_code="42820")
    assert route.called


@respx.mock
def test_get_zoning_hits_correct_endpoint():
    route = respx.get(_ZONING_URL).mock(return_value=httpx.Response(200, text=ZONING_XML))
    PublicDataClient().get_zoning(region_code="42820")
    assert route.called


@respx.mock
def test_get_appraised_value_does_not_inject_service_key():
    route = respx.get(_APPRAISED_URL).mock(return_value=httpx.Response(200, text=APPRAISED_XML))
    PublicDataClient().get_appraised_value(region_code="42820")
    params = dict(route.calls[0].request.url.params)
    assert "serviceKey" not in params


@respx.mock
def test_get_standard_price_hits_correct_endpoint():
    route = respx.get(_STANDARD_URL).mock(return_value=httpx.Response(200, text=STANDARD_PRICE_XML))
    PublicDataClient().get_standard_price(region_code="42820")
    assert route.called


@respx.mock
def test_get_building_registry_hits_correct_endpoint():
    route = respx.get(_REGISTRY_URL).mock(return_value=httpx.Response(200, text=REGISTRY_XML))
    PublicDataClient().get_building_registry(region_code="42820")
    assert route.called


@respx.mock
def test_get_building_map_hits_correct_endpoint():
    route = respx.get(_MAP_URL).mock(return_value=httpx.Response(200, text=REGISTRY_XML))
    PublicDataClient().get_building_map(region_code="42820")
    assert route.called


@respx.mock
def test_raises_rate_limit():
    respx.get(_LAND_SALES_URL).mock(return_value=httpx.Response(200, text=RATE_LIMIT_XML))
    with pytest.raises(RateLimitError):
        PublicDataClient().get_land_sales(region_code="42820", year_month="202403")


@respx.mock
def test_raises_api_key_error():
    respx.get(_LAND_SALES_URL).mock(return_value=httpx.Response(200, text=INVALID_KEY_XML))
    with pytest.raises(APIKeyError):
        PublicDataClient().get_land_sales(region_code="42820", year_month="202403")


@respx.mock
def test_raises_on_http_error():
    respx.get(_LAND_SALES_URL).mock(return_value=httpx.Response(400, text="bad request"))
    with pytest.raises(APIResponseError):
        PublicDataClient().get_land_sales(region_code="42820", year_month="202403")
