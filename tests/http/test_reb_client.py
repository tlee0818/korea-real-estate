"""Tests for RebClient."""

import pytest
import respx
import httpx

from korea_realestate.http.reb import RebClient
from korea_realestate.exceptions import RateLimitError, APIKeyError

from tests.conftest import TRENDS_XML, RATE_LIMIT_XML, INVALID_KEY_XML

_URL = "https://www.reb.or.kr/r-one/openapi/SttsApiTblData.do"


@respx.mock
def test_get_price_trends_hits_correct_endpoint():
    route = respx.get(_URL).mock(return_value=httpx.Response(200, text=TRENDS_XML))
    RebClient().get_price_trends(region_code="42820", index_type="land")
    assert route.called


@respx.mock
def test_get_price_trends_injects_key_param():
    route = respx.get(_URL).mock(return_value=httpx.Response(200, text=TRENDS_XML))
    RebClient().get_price_trends(region_code="42820", index_type="land")
    assert "KEY" in dict(route.calls[0].request.url.params)


@respx.mock
def test_get_price_trends_filters_none_params():
    route = respx.get(_URL).mock(return_value=httpx.Response(200, text=TRENDS_XML))
    RebClient().get_price_trends(region_code="42820", index_type="land",
                                  start_year_month=None, end_year_month=None)
    params = dict(route.calls[0].request.url.params)
    assert "startPeriod" not in params
    assert "endPeriod" not in params


def test_get_price_trends_invalid_index_type():
    with pytest.raises(ValueError, match="index_type"):
        RebClient().get_price_trends(region_code="42820", index_type="invalid")


@respx.mock
def test_raises_rate_limit():
    respx.get(_URL).mock(return_value=httpx.Response(200, text=RATE_LIMIT_XML))
    with pytest.raises(RateLimitError):
        RebClient().get_price_trends(region_code="42820", index_type="land")


@respx.mock
def test_raises_api_key_error():
    respx.get(_URL).mock(return_value=httpx.Response(200, text=INVALID_KEY_XML))
    with pytest.raises(APIKeyError):
        RebClient().get_price_trends(region_code="42820", index_type="land")
