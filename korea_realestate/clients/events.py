"""EventsClient — single source of truth for all historical transaction and permit data."""

from __future__ import annotations

from decimal import Decimal
from typing import Optional

import pandas as pd

from .. import config
from ..http.public_data import PublicDataClient

_LAND_CATEGORY_ALIASES: dict[str, str] = {
    "forest": "임", "임야": "임",
    "field": "전",
    "rice_field": "답",
    "residential": "대", "대지": "대",
    "road": "도", "도로": "도",
    "orchard": "과",
    "factory": "공", "공장": "공",
}

_COMMERCIAL_TYPE_ALIASES: dict[str, str] = {
    "commercial": "상업용", "상업용": "상업용",
    "warehouse": "창고", "창고": "창고",
    "factory": "공장", "공장": "공장",
}


def _parse_price(raw: str | None) -> int:
    if not raw:
        return 0
    return int(str(raw).replace(",", "").strip())


def _parse_area(raw: str | None) -> Decimal:
    if not raw:
        return Decimal("0")
    return Decimal(str(raw).replace(",", "").strip())


def _apply_limit(df: pd.DataFrame, date_col: str, limit: Optional[int]) -> pd.DataFrame:
    if df.empty or limit is None:
        return df
    return df.sort_values(date_col, ascending=False).head(limit).reset_index(drop=True)


class EventsClient:
    """
    All raw historical transaction and permit events.
    Calls PublicDataClient (apis.data.go.kr). No domain logic — returns tidy DataFrames.
    """

    def __init__(self, http: Optional[PublicDataClient] = None):
        self._http = http or PublicDataClient()

    # ------------------------------------------------------------------
    # Land sales
    # ------------------------------------------------------------------

    def get_land_sales(
        self,
        region_code: Optional[str] = None,
        start_year_month: Optional[str] = None,
        end_year_month: Optional[str] = None,
        land_category: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Past land sale transactions (토지 매매 실거래가 — MOLIT).

        Args:
            region_code: 5-digit 시군구 code.
            start_year_month: Range start (YYYYMM or YYYY-MM). Required if year_month omitted.
            end_year_month: Range end inclusive.
            land_category: Filter — Korean char (임/전/대…) or alias (forest/field/residential…).
            limit: Return at most N most-recent rows. None = all.
        """
        from ..utils.date_utils import iter_months, to_year_month

        region = region_code or config.DEFAULT_REGION_CODE
        if not start_year_month or not end_year_month:
            raise ValueError("Both start_year_month and end_year_month required.")

        months = list(iter_months(start_year_month, end_year_month))
        category_filter = _LAND_CATEGORY_ALIASES.get(land_category or "", land_category) if land_category else None

        frames: list[pd.DataFrame] = []
        for ym in months:
            raw = self._http.get_land_sales(region_code=region, year_month=to_year_month(ym))
            df = self._parse_land_sales(raw)
            if not df.empty:
                frames.append(df)

        if not frames:
            return pd.DataFrame()

        result = pd.concat(frames, ignore_index=True)
        if category_filter:
            result = result[result["land_category"].str.contains(category_filter, na=False)]

        return _apply_limit(result, "deal_date", limit)

    def _parse_land_sales(self, data: dict) -> pd.DataFrame:
        body = data.get("response", {}).get("body", {})
        if int(body.get("totalCount", 0)) == 0:
            return pd.DataFrame()
        raw_items = body.get("items", {}).get("item", [])
        if isinstance(raw_items, dict):
            raw_items = [raw_items]

        rows = []
        for item in raw_items:
            year = item.get("dealYear", "")
            month = str(item.get("dealMonth", "")).zfill(2)
            day = str(item.get("dealDay", "")).zfill(2)
            price_raw = _parse_price(item.get("dealAmount"))
            area = _parse_area(item.get("area"))
            price_per_sqm = round(Decimal(price_raw) / area, 2) if area > 0 else None
            rows.append({
                "deal_date": f"{year}-{month}-{day}",
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

    # ------------------------------------------------------------------
    # Commercial / warehouse / factory sales
    # ------------------------------------------------------------------

    def get_commercial_sales(
        self,
        region_code: Optional[str] = None,
        start_year_month: Optional[str] = None,
        end_year_month: Optional[str] = None,
        property_type: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Past commercial/warehouse/factory sales (상업업무용·공장창고 매매 실거래가 — MOLIT).

        Args:
            region_code: 5-digit 시군구 code.
            start_year_month: Range start (YYYYMM or YYYY-MM).
            end_year_month: Range end inclusive.
            property_type: Filter — "상업용", "공장", "창고" (or English aliases).
            limit: Return at most N most-recent rows. None = all.
        """
        from ..utils.date_utils import iter_months, to_year_month

        region = region_code or config.DEFAULT_REGION_CODE
        if not start_year_month or not end_year_month:
            raise ValueError("Both start_year_month and end_year_month required.")

        months = list(iter_months(start_year_month, end_year_month))
        type_filter = _COMMERCIAL_TYPE_ALIASES.get(property_type or "", property_type) if property_type else None

        frames: list[pd.DataFrame] = []
        for ym in months:
            raw = self._http.get_commercial_sales(region_code=region, year_month=to_year_month(ym))
            df = self._parse_commercial_sales(raw)
            if not df.empty:
                frames.append(df)

        if not frames:
            return pd.DataFrame()

        result = pd.concat(frames, ignore_index=True)
        if type_filter:
            result = result[result["building_use"].str.contains(type_filter, na=False)]

        return _apply_limit(result, "deal_date", limit)

    def _parse_commercial_sales(self, data: dict) -> pd.DataFrame:
        body = data.get("response", {}).get("body", {})
        if int(body.get("totalCount", 0)) == 0:
            return pd.DataFrame()
        raw_items = body.get("items", {}).get("item", [])
        if isinstance(raw_items, dict):
            raw_items = [raw_items]

        rows = []
        for item in raw_items:
            year = item.get("dealYear", "")
            month = str(item.get("dealMonth", "")).zfill(2)
            day = str(item.get("dealDay", "")).zfill(2)
            land_area = _parse_area(item.get("landArea", item.get("platArea")))
            bldg_area = _parse_area(item.get("buildingArea", item.get("totArea")))
            price_raw = _parse_price(item.get("dealAmount"))
            price_per_sqm = round(Decimal(price_raw) / bldg_area, 2) if bldg_area > 0 else None
            rows.append({
                "deal_date": f"{year}-{month}-{day}",
                "region": item.get("siGunGu", "").strip(),
                "dong": item.get("umdNm", "").strip(),
                "building_use": item.get("buildingUse", item.get("mainPurpsCdNm", "")).strip(),
                "land_area_sqm": float(land_area),
                "building_area_sqm": float(bldg_area),
                "floors": item.get("floors", item.get("grndFlrCnt")),
                "built_year": item.get("buildYear", item.get("useAprDay", ""))[:4] if item.get("buildYear") or item.get("useAprDay") else None,
                "price_10k_won": price_raw,
                "price_per_sqm": float(price_per_sqm) if price_per_sqm else None,
            })
        return pd.DataFrame(rows)

    # ------------------------------------------------------------------
    # Building permit history
    # ------------------------------------------------------------------

    def get_permit_history(
        self,
        region_code: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        permit_type: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Past building permits: new builds, renovations, demolitions (건축인허가 — MOLIT).

        Args:
            region_code: 5-digit 시군구 code.
            start_date: YYYYMMDD (optional).
            end_date: YYYYMMDD (optional).
            permit_type: "신축", "증축", "대수선", "철거" (optional filter).
            limit: Return at most N most-recent rows. None = all.
        """
        region = region_code or config.DEFAULT_REGION_CODE

        raw = self._http.get_permit_history(
            region_code=region,
            start_date=start_date,
            end_date=end_date,
        )
        df = self._parse_permit_history(raw)

        if permit_type and not df.empty:
            df = df[df["permit_type"].str.contains(permit_type, na=False)]

        return _apply_limit(df, "permit_date", limit)

    def _parse_permit_history(self, data: dict) -> pd.DataFrame:
        body = data.get("response", {}).get("body", {})
        if int(body.get("totalCount", 0)) == 0:
            return pd.DataFrame()
        raw_items = body.get("items", {}).get("item", [])
        if isinstance(raw_items, dict):
            raw_items = [raw_items]

        rows = []
        for item in raw_items:
            rows.append({
                "address": item.get("platPlc", "").strip(),
                "permit_type": item.get("archGbCdNm", "").strip(),
                "main_use": item.get("mainPurpsCdNm", "").strip(),
                "land_area_sqm": float(_parse_area(item.get("platArea"))),
                "building_area_sqm": float(_parse_area(item.get("archArea"))),
                "floor_area_ratio": float(_parse_area(item.get("vlRat"))) if item.get("vlRat") else None,
                "coverage_ratio": float(_parse_area(item.get("bcRat"))) if item.get("bcRat") else None,
                "permit_date": item.get("pmsDay", "").strip(),
                "start_date": item.get("stcnsDay", "").strip() or None,
                "approval_date": item.get("useAprDay", "").strip() or None,
            })
        return pd.DataFrame(rows)
