"""Tests for JusoClient."""

import pytest
import respx
import httpx

from korea_realestate.http.juso import JusoClient
from korea_realestate.exceptions import APIResponseError

from tests.conftest import ADDRESS_JSON

_URL = "https://business.juso.go.kr/addrlink/addrLinkApi.do"


@respx.mock
def test_resolve_address_hits_correct_endpoint():
    route = respx.get(_URL).mock(return_value=httpx.Response(200, text=ADDRESS_JSON))
    JusoClient().resolve_address(keyword="고성군 대진리")
    assert route.called


@respx.mock
def test_resolve_address_injects_confm_key():
    route = respx.get(_URL).mock(return_value=httpx.Response(200, text=ADDRESS_JSON))
    JusoClient().resolve_address(keyword="고성군 대진리")
    assert "confmKey" in dict(route.calls[0].request.url.params)


@respx.mock
def test_resolve_address_injects_json_result_type():
    route = respx.get(_URL).mock(return_value=httpx.Response(200, text=ADDRESS_JSON))
    JusoClient().resolve_address(keyword="고성군 대진리")
    assert dict(route.calls[0].request.url.params).get("resultType") == "json"


@respx.mock
def test_resolve_address_passes_keyword():
    route = respx.get(_URL).mock(return_value=httpx.Response(200, text=ADDRESS_JSON))
    JusoClient().resolve_address(keyword="고성군 대진리")
    assert dict(route.calls[0].request.url.params).get("keyword") == "고성군 대진리"


@respx.mock
def test_raises_on_http_error():
    respx.get(_URL).mock(return_value=httpx.Response(500, text="error"))
    with pytest.raises(APIResponseError):
        JusoClient().resolve_address(keyword="고성군")
