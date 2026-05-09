"""Zoning and land use classification (토지이용계획 — MOLIT)."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Optional

import pandas as pd

from ..base_client import BaseClient
from ..config import DEFAULT_REGION_CODE
from ..exceptions import APIKeyError, RegionNotFoundError

_ENDPOINT = "https://apis.data.go.kr/1613000/LandUseService/getLandUseList"


def _safe_decimal(val: str | None) -> Optional[Decimal]:
    if not val:
        return None
    try:
        return Decimal(str(val).replace(",", "").strip())
    except InvalidOperation:
        return None


class ZoningClient(BaseClient):
    """
    Client for querying zoning classifications and land use categories.
    Returns 용도지역 (zoning class) and 지목 (land category) for parcels.
    """

    def __init__(
        self,
        api_key: str,
        default_region: Optional[str] = None,
    ):
        """
        Args:
            api_key: Service key for the Zoning & Land Use API.
                     Obtain at https://www.data.go.kr/data/15113034/openapi.do
            default_region: Fallback 5-digit 시군구 code when region_code is omitted.
        """
        if not api_key:
            raise APIKeyError(
                "ZoningClient requires an api_key. "
                "Obtain one at https://www.data.go.kr/data/15113034/openapi.do "
                "and pass it as ZoningClient(api_key='...')."
            )
        super().__init__(api_key)
        self._default_region = default_region or DEFAULT_REGION_CODE

    def get_zoning(
        self,
        region_code: Optional[str] = None,
        dong: Optional[str] = None,
        num_rows: int = 1000,
    ) -> pd.DataFrame:
        """
        Fetch zoning and land use classification for a region.

        Args:
            region_code: 5-digit 시군구 code. Falls back to DEFAULT_REGION_CODE.
            dong: Optional subdivision (읍·면·동) name to narrow results.
            num_rows: Max rows per API call.
        """
        region = region_code or self._default_region

        params = self._build_params({
            "pnu": region,
            "umdNm": dong,
            "numOfRows": num_rows,
            "pageNo": 1,
        })

        data = self._get(_ENDPOINT, params)
        rows = self._extract_rows(data, region)

        if not rows:
            raise RegionNotFoundError(
                f"No zoning data found for region {region}"
                + (f" dong '{dong}'." if dong else ".")
            )

        df = pd.DataFrame(rows).reset_index(drop=True)

        if dong:
            df = df[df["dong"].str.contains(dong, na=False)]

        return df

    def _extract_rows(self, data: dict, region: str) -> list[dict]:
        body = data.get("response", {}).get("body", {})
        raw_items = body.get("items", {}).get("item", [])
        if isinstance(raw_items, dict):
            raw_items = [raw_items]

        rows = []
        for item in raw_items:
            rows.append({
                "region": item.get("sigunguCd", region),
                "dong": item.get("umdNm", "").strip(),
                "parcel": item.get("jibun", "").strip(),
                "land_category": item.get("lndcgrCodeNm", item.get("landCdNm", "")).strip(),
                "zoning_class": item.get("prposAreaDstrcNm", item.get("landUseNm", "")).strip(),
                "zoning_detail": item.get("prposAreaDstrcNo", "").strip(),
                "area_sqm": _safe_decimal(item.get("lndpclAr", item.get("area"))),
                "restrictions": item.get("etc", item.get("restriction", "")).strip() or None,
            })
        return rows
