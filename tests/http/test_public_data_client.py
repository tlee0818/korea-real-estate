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

_LAND_SALES_URL    = "https://apis.data.go.kr/1613000/RTMSDataSvcLandTrade/getRTMSDataSvcLandTrade"
_COMMERCIAL_URL    = "https://apis.data.go.kr/1613000/RTMSDataSvcNrgTrade/getRTMSDataSvcNrgTrade"
_PERMIT_URL        = "https://apis.data.go.kr/1613000/ArchPmsService/getApBasisOulnInfo"
_ZONING_URL        = "https://apis.data.go.kr/1613000/LandUseService/getLandUseList"
_APPRAISED_URL     = "https://apis.data.go.kr/1611000/nsdi/IndvdLandPriceService/wfs/IndvdLandPrice"
_STANDARD_URL      = "https://apis.data.go.kr/1613000/PubLandPriceService/getPblcLandPriceList"
_REGISTRY_URL      = "https://apis.data.go.kr/1613000/ArchPmsService/getApBdInfo"
_MAP_URL           = "https://apis.data.go.kr/1613000/NSYDPnbldService/getNSYDPnbld"


@respx.mock
def test_land_trade_history_hits_correct_endpoint():
    route = respx.get(_LAND_SALES_URL).mock(return_value=httpx.Response(200, text=SALES_XML))
    PublicDataClient().land_trade_history(region_code="42820", year_month="202403")
    assert route.called


@respx.mock
def test_land_trade_history_injects_service_key():
    route = respx.get(_LAND_SALES_URL).mock(return_value=httpx.Response(200, text=SALES_XML))
    PublicDataClient().land_trade_history(region_code="42820", year_month="202403")
    assert "serviceKey" in dict(route.calls[0].request.url.params)


@respx.mock
def test_commercial_trade_history_hits_correct_endpoint():
    route = respx.get(_COMMERCIAL_URL).mock(return_value=httpx.Response(200, text=COMMERCIAL_XML))
    PublicDataClient().commercial_trade_history(region_code="42820", year_month="202403")
    assert route.called


@respx.mock
def test_building_permit_records_hits_correct_endpoint():
    route = respx.get(_PERMIT_URL).mock(return_value=httpx.Response(200, text=PERMIT_XML))
    PublicDataClient().building_permit_records(region_code="42820")
    assert route.called


@respx.mock
def test_land_use_zoning_hits_correct_endpoint():
    route = respx.get(_ZONING_URL).mock(return_value=httpx.Response(200, text=ZONING_XML))
    PublicDataClient().land_use_zoning(region_code="42820")
    assert route.called


@respx.mock
def test_individual_land_price_does_not_inject_service_key():
    route = respx.get(_APPRAISED_URL).mock(return_value=httpx.Response(200, text=APPRAISED_XML))
    PublicDataClient().individual_land_price(region_code="42820")
    params = dict(route.calls[0].request.url.params)
    assert "serviceKey" not in params


@respx.mock
def test_standard_land_price_hits_correct_endpoint():
    route = respx.get(_STANDARD_URL).mock(return_value=httpx.Response(200, text=STANDARD_PRICE_XML))
    PublicDataClient().standard_land_price(region_code="42820")
    assert route.called


@respx.mock
def test_building_ledger_hits_correct_endpoint():
    route = respx.get(_REGISTRY_URL).mock(return_value=httpx.Response(200, text=REGISTRY_XML))
    PublicDataClient().building_ledger(region_code="42820")
    assert route.called


@respx.mock
def test_building_spatial_info_hits_correct_endpoint():
    route = respx.get(_MAP_URL).mock(return_value=httpx.Response(200, text=REGISTRY_XML))
    PublicDataClient().building_spatial_info(region_code="42820")
    assert route.called


@respx.mock
def test_raises_rate_limit():
    respx.get(_LAND_SALES_URL).mock(return_value=httpx.Response(200, text=RATE_LIMIT_XML))
    with pytest.raises(RateLimitError):
        PublicDataClient().land_trade_history(region_code="42820", year_month="202403")


@respx.mock
def test_raises_api_key_error():
    respx.get(_LAND_SALES_URL).mock(return_value=httpx.Response(200, text=INVALID_KEY_XML))
    with pytest.raises(APIKeyError):
        PublicDataClient().land_trade_history(region_code="42820", year_month="202403")


@respx.mock
def test_raises_on_http_error():
    respx.get(_LAND_SALES_URL).mock(return_value=httpx.Response(400, text="bad request"))
    with pytest.raises(APIResponseError):
        PublicDataClient().land_trade_history(region_code="42820", year_month="202403")
