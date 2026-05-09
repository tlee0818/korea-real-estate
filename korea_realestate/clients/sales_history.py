"""Past land sale transactions (토지 매매 실거래가 — MOLIT)."""

from __future__ import annotations

from decimal import Decimal
from typing import Optional

import pandas as pd

from ..base_client import BaseClient
from ..config import DEFAULT_REGION_CODE
from ..exceptions import APIKeyError, RegionNotFoundError
from ..utils.date_utils import iter_months, to_year_month

_ENDPOINT = "https://apis.data.go.kr/1613000/RTMSDataSvcLandTrade/getRTMSDataSvcLandTrade"

# Korean field → English column mapping
_FIELD_MAP = {
    "dealYear": "deal_year",
    "dealMonth": "deal_month",
    "dealDay": "deal_day",
    "siGunGu": "region",
    "umdNm": "dong",
    "jibun": "parcel",
    "landCd": "land_category_code",
    "landCdNm": "land_category",
    "officialLandPrice": "official_land_price",
    "dealAmount": "price_10k_won_raw",
    "area": "area_sqm",
    "landUse": "zoning",
    "buyerGbn": "buyer_type",
    "cdealType": "cancel_type",
    "cdealDay": "cancel_date",
}

# Korean land category aliases → canonical Korean character
_LAND_CATEGORY_ALIASES: dict[str, str] = {
    "forest": "임",
    "임야": "임",
    "field": "전",
    "rice_field": "답",
    "residential": "대",
    "대지": "대",
    "road": "도",
    "도로": "도",
    "orchard": "과",
    "factory": "공",
    "공장": "공",
}


def _parse_price(raw: str | None) -> int:
    """Strip commas/whitespace and convert to int."""
    if not raw:
        return 0
    return int(str(raw).replace(",", "").strip())


def _parse_area(raw: str | None) -> Decimal:
    if not raw:
        return Decimal("0")
    return Decimal(str(raw).replace(",", "").strip())


def _items_to_df(items: list[dict]) -> pd.DataFrame:
    rows = []
    for item in items:
        year = item.get("dealYear", "")
        month = str(item.get("dealMonth", "")).zfill(2)
        day = str(item.get("dealDay", "")).zfill(2)
        deal_date = f"{year}-{month}-{day}"

        price_raw = _parse_price(item.get("dealAmount"))
        area = _parse_area(item.get("area"))
        price_per_sqm = round(Decimal(price_raw) / area, 2) if area > 0 else None

        rows.append({
            "deal_date": deal_date,
            "region": item.get("siGunGu", "").strip(),
            "dong": item.get("umdNm", "").strip(),
            "parcel": item.get("jibun", "").strip(),
            "land_category": item.get("landCdNm", item.get("landCd", "")).strip(),
            "area_sqm": float(area),
            "price_10k_won": price_raw,
            "price_per_sqm": float(price_per_sqm) if price_per_sqm else None,
            "zoning": item.get("landUse", "").strip(),
            "buyer_type": item.get("buyerGbn", "").strip(),
            "cancelled": bool(item.get("cdealType", "")),
        })

    return pd.DataFrame(rows)


class SalesHistoryClient(BaseClient):
    """
    Client for querying past land sale transactions.
    All transactions are government-reported (실거래가).
    """

    def __init__(
        self,
        api_key: str,
        default_region: Optional[str] = None,
    ):
        """
        Args:
            api_key: Service key for the Land Sales History API.
                     Obtain at https://www.data.go.kr/data/15126466/openapi.do
            default_region: Fallback 5-digit 시군구 code when region_code is omitted.
        """
        if not api_key:
            raise APIKeyError(
                "SalesHistoryClient requires an api_key. "
                "Obtain one at https://www.data.go.kr/data/15126466/openapi.do "
                "and pass it as SalesHistoryClient(api_key='...')."
            )
        super().__init__(api_key)
        self._default_region = default_region or DEFAULT_REGION_CODE

    def get_sales(
        self,
        region_code: Optional[str] = None,
        year_month: Optional[str] = None,
        start_year_month: Optional[str] = None,
        end_year_month: Optional[str] = None,
        land_category: Optional[str] = None,
        num_rows: int = 1000,
    ) -> pd.DataFrame:
        """
        Fetch past land sale transactions for a region and time range.

        Args:
            region_code: 5-digit 시군구 code. Falls back to DEFAULT_REGION_CODE.
            year_month: Single month to query (YYYYMM or YYYY-MM).
            start_year_month: Start of date range (inclusive).
            end_year_month: End of date range (inclusive).
            land_category: Filter by land category. Accepts Korean char (임, 전, 대…)
                           or English alias (forest, field, residential…).
            num_rows: Max rows per API call.
        """
        region = region_code or self._default_region

        if year_month:
            months = [to_year_month(year_month)]
        elif start_year_month and end_year_month:
            months = list(iter_months(start_year_month, end_year_month))
        else:
            raise ValueError("Provide either 'year_month' or both 'start_year_month' and 'end_year_month'.")

        # Resolve land category alias
        category_filter: Optional[str] = None
        if land_category:
            category_filter = _LAND_CATEGORY_ALIASES.get(land_category, land_category)

        frames: list[pd.DataFrame] = []
        for ym in months:
            df = self._fetch_month(region, ym, num_rows)
            if not df.empty:
                frames.append(df)

        if not frames:
            raise RegionNotFoundError(
                f"No land sales found for region {region} in the requested period."
            )

        result = pd.concat(frames, ignore_index=True)

        if category_filter:
            result = result[result["land_category"].str.contains(category_filter, na=False)]

        return result.sort_values("deal_date").reset_index(drop=True)

    def _fetch_month(self, region_code: str, year_month: str, num_rows: int) -> pd.DataFrame:
        params = self._build_params({
            "LAWD_CD": region_code,
            "DEAL_YMD": year_month,
            "numOfRows": num_rows,
            "pageNo": 1,
        })
        data = self._get(_ENDPOINT, params)

        body = data.get("response", {}).get("body", {})
        total_count = int(body.get("totalCount", 0))
        if total_count == 0:
            return pd.DataFrame()

        raw_items = body.get("items", {}).get("item", [])
        if isinstance(raw_items, dict):
            raw_items = [raw_items]

        return _items_to_df(raw_items)
