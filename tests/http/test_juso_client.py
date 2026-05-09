"""Tests for JusoClient."""

import httpx
import pytest
import respx

from korea_realestate.exceptions import APIResponseError
from korea_realestate.http.juso import JusoClient
from tests.conftest import ADDRESS_JSON

_URL = "https://business.juso.go.kr/addrlink/addrLinkApi.do"


@respx.mock
def test_address_lookup_hits_correct_endpoint():
    route = respx.get(_URL).mock(return_value=httpx.Response(200, text=ADDRESS_JSON))
    JusoClient().address_lookup(keyword="고성군 대진리")
    assert route.called


@respx.mock
def test_address_lookup_injects_confm_key():
    route = respx.get(_URL).mock(return_value=httpx.Response(200, text=ADDRESS_JSON))
    JusoClient().address_lookup(keyword="고성군 대진리")
    assert "confmKey" in dict(route.calls[0].request.url.params)


@respx.mock
def test_address_lookup_injects_json_result_type():
    route = respx.get(_URL).mock(return_value=httpx.Response(200, text=ADDRESS_JSON))
    JusoClient().address_lookup(keyword="고성군 대진리")
    assert dict(route.calls[0].request.url.params).get("resultType") == "json"


@respx.mock
def test_address_lookup_passes_keyword():
    route = respx.get(_URL).mock(return_value=httpx.Response(200, text=ADDRESS_JSON))
    JusoClient().address_lookup(keyword="고성군 대진리")
    assert dict(route.calls[0].request.url.params).get("keyword") == "고성군 대진리"


@respx.mock
def test_raises_on_http_error():
    respx.get(_URL).mock(return_value=httpx.Response(500, text="error"))
    with pytest.raises(APIResponseError):
        JusoClient().address_lookup(keyword="고성군")
