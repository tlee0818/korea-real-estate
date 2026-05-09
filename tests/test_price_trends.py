import pytest
import respx
import httpx
from decimal import Decimal

from korea_realestate.clients import PriceTrendsClient
from korea_realestate.exceptions import APIKeyError, RateLimitError

from .conftest import FAKE_KEY, FAKE_REGION, TRENDS_XML, RATE_LIMIT_XML, INVALID_KEY_XML

_ENDPOINT = "https://www.reb.or.kr/r-one/openapi/SttsApiTblData.do"


def test_requires_api_key():
    with pytest.raises(APIKeyError, match="api_key"):
        PriceTrendsClient(api_key="")


def test_invalid_index_type():
    client = PriceTrendsClient(api_key=FAKE_KEY)
    with pytest.raises(ValueError, match="index_type"):
        client.get_trend_index(index_type="invalid", region_code=FAKE_REGION)


@respx.mock
def test_get_land_trend():
    respx.get(_ENDPOINT).mock(return_value=httpx.Response(200, text=TRENDS_XML))

    client = PriceTrendsClient(api_key=FAKE_KEY)
    df = client.get_trend_index(
        index_type="land",
        region_code=FAKE_REGION,
        start_year_month="202403",
        end_year_month="202403",
    )

    assert len(df) == 1
    assert df.iloc[0]["period"] == "202403"
    assert df.iloc[0]["index_value"] == Decimal("101.5")
    assert df.iloc[0]["change_pct_mom"] == Decimal("0.3")


@respx.mock
def test_rate_limit_raises():
    respx.get(_ENDPOINT).mock(return_value=httpx.Response(200, text=RATE_LIMIT_XML))

    client = PriceTrendsClient(api_key=FAKE_KEY)
    with pytest.raises(RateLimitError):
        client.get_trend_index(index_type="land", region_code=FAKE_REGION)
