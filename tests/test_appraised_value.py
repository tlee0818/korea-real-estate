import pytest
import respx
import httpx

from korea_realestate.clients import AppraisedValueClient
from korea_realestate.exceptions import APIKeyError, RateLimitError

from .conftest import FAKE_KEY, FAKE_REGION, APPRAISED_XML, RATE_LIMIT_XML, INVALID_KEY_XML

_ENDPOINT = "https://apis.data.go.kr/1611000/nsdi/IndvdLandPriceService/wfs/IndvdLandPrice"


def test_requires_api_key():
    with pytest.raises(APIKeyError, match="api_key"):
        AppraisedValueClient(api_key="")


@respx.mock
def test_get_appraised_value():
    respx.get(_ENDPOINT).mock(return_value=httpx.Response(200, text=APPRAISED_XML))

    client = AppraisedValueClient(api_key=FAKE_KEY)
    df = client.get_appraised_value(region_code=FAKE_REGION, year=2024)

    assert len(df) == 1
    row = df.iloc[0]
    assert row["dong"] == "대진리"
    assert row["value_per_sqm"] == 50000
    assert row["area_sqm"] == 500.0
    assert row["total_value"] == 50000 * 500
    assert row["reference_year"] == 2024


@respx.mock
def test_rate_limit_raises():
    respx.get(_ENDPOINT).mock(return_value=httpx.Response(200, text=RATE_LIMIT_XML))

    client = AppraisedValueClient(api_key=FAKE_KEY)
    with pytest.raises(RateLimitError):
        client.get_appraised_value(region_code=FAKE_REGION)
