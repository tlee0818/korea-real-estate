"""Market price trend indices (한국부동산원 통계 — REB)."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Optional

import pandas as pd

from ..base_client import BaseClient
from ..config import DEFAULT_REGION_CODE
from ..exceptions import APIKeyError, RegionNotFoundError
from ..utils.date_utils import to_year_month

_ENDPOINT = "https://www.reb.or.kr/r-one/openapi/SttsApiTblData.do"

# Table IDs for the two supported indices
_TABLE_IDS = {
    "land": "TBL_LND_CHGRT",
    "housing": "TBL_HSG_PRICE",
}


def _safe_decimal(val: str | None) -> Optional[Decimal]:
    if not val:
        return None
    try:
        return Decimal(str(val).replace(",", "").strip())
    except InvalidOperation:
        return None


class PriceTrendsClient(BaseClient):
    """
    Client for querying land price change rate and housing price trend indices.
    """

    def __init__(
        self,
        api_key: str,
        default_region: Optional[str] = None,
    ):
        """
        Args:
            api_key: Service key for the Market Price Trends API.
                     Obtain at https://www.data.go.kr/data/15134761/openapi.do
            default_region: Fallback 5-digit 시군구 code when region_code is omitted.
        """
        if not api_key:
            raise APIKeyError(
                "PriceTrendsClient requires an api_key. "
                "Obtain one at https://www.data.go.kr/data/15134761/openapi.do "
                "and pass it as PriceTrendsClient(api_key='...')."
            )
        super().__init__(api_key)
        self._default_region = default_region or DEFAULT_REGION_CODE

    def get_trend_index(
        self,
        index_type: str = "land",
        region_code: Optional[str] = None,
        start_year_month: Optional[str] = None,
        end_year_month: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Fetch price trend index for a region and time range.

        Args:
            index_type: "land" (지가변동률) or "housing" (주택가격동향).
            region_code: 5-digit 시군구 code. Falls back to DEFAULT_REGION_CODE.
            start_year_month: Start period (YYYYMM or YYYY-MM).
            end_year_month: End period (YYYYMM or YYYY-MM).
        """
        if index_type not in _TABLE_IDS:
            raise ValueError(f"index_type must be 'land' or 'housing', got '{index_type}'.")

        region = region_code or self._default_region
        start = to_year_month(start_year_month) if start_year_month else None
        end = to_year_month(end_year_month) if end_year_month else None

        params = self._build_params({
            "tblId": _TABLE_IDS[index_type],
            "regionCode": region,
            "startPeriod": start,
            "endPeriod": end,
            "format": "xml",
            "numOfRows": 500,
            "pageNo": 1,
        })

        data = self._get(_ENDPOINT, params)
        rows = self._extract_rows(data, region)

        if not rows:
            raise RegionNotFoundError(
                f"No {index_type} price trend data found for region {region}."
            )

        return pd.DataFrame(rows).sort_values("period").reset_index(drop=True)

    def _extract_rows(self, data: dict, region: str) -> list[dict]:
        body = data.get("response", data).get("body", {})
        raw_items = body.get("items", {}).get("item", [])
        if isinstance(raw_items, dict):
            raw_items = [raw_items]

        rows = []
        for item in raw_items:
            rows.append({
                "period": item.get("period", item.get("PRD_DE", "")),
                "region": item.get("regionNm", item.get("REGION_NM", region)),
                "index_value": _safe_decimal(item.get("indexValue", item.get("INDEX_VALUE"))),
                "change_pct_mom": _safe_decimal(item.get("changeRateMom", item.get("CHG_RT_MOM"))),
                "change_pct_yoy": _safe_decimal(item.get("changeRateYoy", item.get("CHG_RT_YOY"))),
            })
        return rows
