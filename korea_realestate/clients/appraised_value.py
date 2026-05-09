"""Government appraised land value per ㎡ (개별공시지가 — MOLIT/NSDI)."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Optional

import pandas as pd

from ..base_client import BaseClient
from ..config import DEFAULT_REGION_CODE
from ..exceptions import APIKeyError, RegionNotFoundError

_ENDPOINT = "https://apis.data.go.kr/1611000/nsdi/IndvdLandPriceService/wfs/IndvdLandPrice"


def _safe_int(val: str | None) -> Optional[int]:
    if not val:
        return None
    try:
        return int(str(val).replace(",", "").strip())
    except (ValueError, TypeError):
        return None


def _safe_decimal(val: str | None) -> Optional[Decimal]:
    if not val:
        return None
    try:
        return Decimal(str(val).replace(",", "").strip())
    except InvalidOperation:
        return None


class AppraisedValueClient(BaseClient):
    """
    Client for querying official government-appraised land values (개별공시지가).
    Values are used as the basis for property tax calculations.
    """

    def __init__(
        self,
        api_key: str,
        default_region: Optional[str] = None,
    ):
        """
        Args:
            api_key: Service key for the Appraised Land Value API.
                     Obtain at https://www.data.go.kr/data/15057159/openapi.do
            default_region: Fallback 5-digit 시군구 code when region_code is omitted.
        """
        if not api_key:
            raise APIKeyError(
                "AppraisedValueClient requires an api_key. "
                "Obtain one at https://www.data.go.kr/data/15057159/openapi.do "
                "and pass it as AppraisedValueClient(api_key='...')."
            )
        super().__init__(api_key)
        self._default_region = default_region or DEFAULT_REGION_CODE

    def get_appraised_value(
        self,
        region_code: Optional[str] = None,
        year: Optional[int] = None,
        num_rows: int = 1000,
    ) -> pd.DataFrame:
        """
        Fetch government-appraised land values for a region and year.

        Args:
            region_code: 5-digit 시군구 code. Falls back to DEFAULT_REGION_CODE.
            year: Reference year (e.g. 2024). Defaults to most recent available.
            num_rows: Max rows per API call.
        """
        region = region_code or self._default_region

        params = self._build_params({
            "key": self._api_key,
            "pnu": region,
            "stdrYear": str(year) if year else None,
            "numOfRows": num_rows,
            "pageNo": 1,
            "format": "json",
        })
        # The NSDI WFS endpoint uses 'key' instead of 'serviceKey'
        params.pop("serviceKey", None)

        data = self._get(_ENDPOINT, params)
        rows = self._extract_rows(data, region, year)

        if not rows:
            raise RegionNotFoundError(
                f"No appraised value data found for region {region}"
                + (f" year {year}." if year else ".")
            )

        return pd.DataFrame(rows).reset_index(drop=True)

    def _extract_rows(self, data: dict, region: str, year: Optional[int]) -> list[dict]:
        # Handle both standard response envelope and WFS FeatureCollection
        features = (
            data.get("features")
            or data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
        )
        if isinstance(features, dict):
            features = [features]
        if not features:
            return []

        rows = []
        for feat in features:
            props = feat.get("properties", feat)
            area_raw = props.get("lndpclAr", props.get("area"))
            value_per_sqm = _safe_int(props.get("pblntfPclnd", props.get("officialPrice")))
            area = _safe_decimal(area_raw)
            total = (
                int(Decimal(str(value_per_sqm)) * area)
                if value_per_sqm and area
                else None
            )
            rows.append({
                "region": props.get("sigCd", region),
                "dong": props.get("emdCd", props.get("umdNm", "")),
                "parcel": props.get("mnnmSlno", props.get("jibun", "")),
                "area_sqm": float(area) if area else None,
                "value_per_sqm": value_per_sqm,
                "total_value": total,
                "reference_year": int(props.get("stdrYear", year or 0)) or None,
            })
        return rows
