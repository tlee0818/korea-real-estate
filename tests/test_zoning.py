import pytest
import respx
import httpx

from korea_realestate.clients import ZoningClient
from korea_realestate.exceptions import APIKeyError, RateLimitError

from .conftest import FAKE_KEY, FAKE_REGION, ZONING_XML, RATE_LIMIT_XML

_ENDPOINT = "https://apis.data.go.kr/1613000/LandUseService/getLandUseList"


def test_requires_api_key():
    with pytest.raises(APIKeyError, match="api_key"):
        ZoningClient(api_key="")


@respx.mock
def test_get_zoning():
    respx.get(_ENDPOINT).mock(return_value=httpx.Response(200, text=ZONING_XML))

    client = ZoningClient(api_key=FAKE_KEY)
    df = client.get_zoning(region_code=FAKE_REGION)

    assert len(df) == 1
    row = df.iloc[0]
    assert row["dong"] == "대진리"
    assert row["land_category"] == "임"
    assert row["zoning_class"] == "계획관리지역"
    assert float(row["area_sqm"]) == 500.0


@respx.mock
def test_dong_filter():
    respx.get(_ENDPOINT).mock(return_value=httpx.Response(200, text=ZONING_XML))

    client = ZoningClient(api_key=FAKE_KEY)
    df = client.get_zoning(region_code=FAKE_REGION, dong="대진리")
    assert len(df) == 1


@respx.mock
def test_rate_limit_raises():
    respx.get(_ENDPOINT).mock(return_value=httpx.Response(200, text=RATE_LIMIT_XML))

    client = ZoningClient(api_key=FAKE_KEY)
    with pytest.raises(RateLimitError):
        client.get_zoning(region_code=FAKE_REGION)
