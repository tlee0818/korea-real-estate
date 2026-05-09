"""Tests for RebClient."""

import httpx
import pytest
import respx

from korea_realestate.exceptions import APIKeyError, RateLimitError
from korea_realestate.http.reb import RebClient
from tests.conftest import REB_DATA_XML, REB_INVALID_KEY_XML, REB_RATE_LIMIT_XML, REB_STATS_XML

_DATA_URL = "https://www.reb.or.kr/r-one/openapi/SttsApiTblData.do"
_TABLE_URL = "https://www.reb.or.kr/r-one/openapi/SttsApiTbl.do"
_ITEM_URL = "https://www.reb.or.kr/r-one/openapi/SttsApiTblItm.do"


# ---------------------------------------------------------------------------
# real_estate_price_index
# ---------------------------------------------------------------------------


@respx.mock
def test_real_estate_price_index_hits_correct_endpoint():
    route = respx.get(_DATA_URL).mock(return_value=httpx.Response(200, text=REB_DATA_XML))
    RebClient().real_estate_price_index(region_code="42820", index_type="land")
    assert route.called


@respx.mock
def test_real_estate_price_index_injects_key_param():
    route = respx.get(_DATA_URL).mock(return_value=httpx.Response(200, text=REB_DATA_XML))
    RebClient().real_estate_price_index(region_code="42820", index_type="land")
    assert "KEY" in dict(route.calls[0].request.url.params)


@respx.mock
def test_real_estate_price_index_filters_none_params():
    route = respx.get(_DATA_URL).mock(return_value=httpx.Response(200, text=REB_DATA_XML))
    RebClient().real_estate_price_index(
        region_code="42820",
        index_type="land",
        start_year_month=None,
        end_year_month=None,
    )
    params = dict(route.calls[0].request.url.params)
    assert "START_WRTTIME" not in params
    assert "END_WRTTIME" not in params


def test_real_estate_price_index_invalid_index_type():
    with pytest.raises(ValueError, match="index_type"):
        RebClient().real_estate_price_index(region_code="42820", index_type="invalid")


@respx.mock
def test_raises_rate_limit():
    respx.get(_DATA_URL).mock(return_value=httpx.Response(200, text=REB_RATE_LIMIT_XML))
    with pytest.raises(RateLimitError):
        RebClient().real_estate_price_index(region_code="42820", index_type="land")


@respx.mock
def test_raises_api_key_error():
    respx.get(_DATA_URL).mock(return_value=httpx.Response(200, text=REB_INVALID_KEY_XML))
    with pytest.raises(APIKeyError):
        RebClient().real_estate_price_index(region_code="42820", index_type="land")


# ---------------------------------------------------------------------------
# statistics_table_list
# ---------------------------------------------------------------------------


@respx.mock
def test_statistics_table_list_hits_correct_endpoint():
    route = respx.get(_TABLE_URL).mock(return_value=httpx.Response(200, text=REB_STATS_XML))
    result = RebClient().statistics_table_list()
    assert route.called
    assert result["total_count"] == 1
    assert result["rows"][0]["STATBL_ID"] == "A_2024_00900"


@respx.mock
def test_statistics_table_list_optional_statbl_id():
    route = respx.get(_TABLE_URL).mock(return_value=httpx.Response(200, text=REB_STATS_XML))
    RebClient().statistics_table_list(statbl_id="A_2024_00900")
    assert "STATBL_ID" in dict(route.calls[0].request.url.params)


# ---------------------------------------------------------------------------
# statistics_item_list
# ---------------------------------------------------------------------------


@respx.mock
def test_statistics_item_list_hits_correct_endpoint():
    route = respx.get(_ITEM_URL).mock(return_value=httpx.Response(200, text=REB_STATS_XML))
    RebClient().statistics_item_list(statbl_id="A_2024_00900")
    assert route.called
    params = dict(route.calls[0].request.url.params)
    assert params["STATBL_ID"] == "A_2024_00900"


# ---------------------------------------------------------------------------
# statistics_data
# ---------------------------------------------------------------------------


@respx.mock
def test_statistics_data_hits_correct_endpoint():
    route = respx.get(_DATA_URL).mock(return_value=httpx.Response(200, text=REB_DATA_XML))
    result = RebClient().statistics_data(statbl_id="A_2024_00900", cycle_code="MM")
    assert route.called
    assert result["rows"][0]["DTA_VAL"] == "101.5"


@respx.mock
def test_statistics_data_passes_required_params():
    route = respx.get(_DATA_URL).mock(return_value=httpx.Response(200, text=REB_DATA_XML))
    RebClient().statistics_data(statbl_id="A_2024_00900", cycle_code="YY")
    params = dict(route.calls[0].request.url.params)
    assert params["STATBL_ID"] == "A_2024_00900"
    assert params["DTACYCLE_CD"] == "YY"
