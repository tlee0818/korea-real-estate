"""LandClient — land parcel data: zoning, appraised value, standard price, sales history."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Optional

import pandas as pd
from dateutil.relativedelta import relativedelta

from .. import config
from ..http.public_data import PublicDataClient
from .address import AddressClient
from .events import EventsClient

def _safe_decimal(val: str | None) -> Optional[Decimal]:
    if not val:
        return None
    try:
        return Decimal(str(val).replace(",", "").strip())
    except InvalidOperation:
        return None


def _safe_int(val: str | None) -> Optional[int]:
    if not val:
        return None
    try:
        return int(str(val).replace(",", "").strip())
    except (ValueError, TypeError):
        return None


class LandClient:
    """
    Land parcel data. Calls zoning, appraised-value, and standard-price APIs directly.
    Delegates all historical sales to EventsClient.
    """

    def __init__(
        self,
        events: Optional[EventsClient] = None,
        address: Optional[AddressClient] = None,
        http: Optional[PublicDataClient] = None,
    ):
        self._http = http or PublicDataClient()
        self._events = events or EventsClient(http=self._http)
        self._address = address or AddressClient()

    # ------------------------------------------------------------------
    # Individual methods
    # ------------------------------------------------------------------

    def get_zoning(
        self,
        region_code: Optional[str] = None,
        dong: Optional[str] = None,
        num_rows: int = 1000,
    ) -> pd.DataFrame:
        """
        Zoning and land-use classification for a region (토지이용계획 — MOLIT).

        Returns: region, dong, parcel, land_category, zoning_class,
                 zoning_detail, area_sqm, restrictions.
        """
        region = region_code or config.DEFAULT_REGION_CODE
        data = self._http.get_zoning(region_code=region, dong=dong, num_rows=num_rows)
        rows = self._parse_zoning(data, region)
        df = pd.DataFrame(rows).reset_index(drop=True)
        if dong and not df.empty:
            df = df[df["dong"].str.contains(dong, na=False)]
        return df.reset_index(drop=True)

    def _parse_zoning(self, data: dict, region: str) -> list[dict]:
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
                "area_sqm": float(_safe_decimal(item.get("lndpclAr", item.get("area"))) or 0),
                "restrictions": item.get("etc", item.get("restriction", "")).strip() or None,
            })
        return rows

    def get_appraised_value(
        self,
        region_code: Optional[str] = None,
        year: Optional[int] = None,
        num_rows: int = 1000,
    ) -> pd.DataFrame:
        """
        Government-appraised land values (개별공시지가 — MOLIT/NSDI).

        Returns: region, dong, parcel, area_sqm, value_per_sqm, total_value, reference_year.
        """
        region = region_code or config.DEFAULT_REGION_CODE
        data = self._http.get_appraised_value(region_code=region, year=year, num_rows=num_rows)

        rows = self._parse_appraised(data, region, year)
        return pd.DataFrame(rows).reset_index(drop=True)

    def _parse_appraised(self, data: dict, region: str, year: Optional[int]) -> list[dict]:
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
            area = _safe_decimal(props.get("lndpclAr", props.get("area")))
            value_per_sqm = _safe_int(props.get("pblntfPclnd", props.get("officialPrice")))
            total = int(Decimal(str(value_per_sqm)) * area) if value_per_sqm and area else None
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

    def get_standard_price(
        self,
        region_code: Optional[str] = None,
        year: Optional[int] = None,
        land_category: Optional[str] = None,
        num_rows: int = 1000,
    ) -> pd.DataFrame:
        """
        Standard reference land price (표준지공시지가 — MOLIT).

        Returns: region, dong, parcel, land_category, area_sqm,
                 price_per_sqm, reference_year, zoning, land_use, terrain, road_access.
        """
        region = region_code or config.DEFAULT_REGION_CODE
        data = self._http.get_standard_price(region_code=region, year=year, num_rows=num_rows)
        rows = self._parse_standard_price(data, region, year)
        df = pd.DataFrame(rows).reset_index(drop=True)
        if land_category and not df.empty:
            df = df[df["land_category"].str.contains(land_category, na=False)]
        return df.reset_index(drop=True)

    def _parse_standard_price(self, data: dict, region: str, year: Optional[int]) -> list[dict]:
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
                "land_category": item.get("lndcgrCodeNm", "").strip(),
                "area_sqm": float(_safe_decimal(item.get("lndpclAr")) or 0),
                "price_per_sqm": _safe_int(item.get("pblntfPclnd")),
                "reference_year": int(item.get("stdrYear", year or 0)) or None,
                "zoning": item.get("prposAreaDstrcNm", "").strip(),
                "land_use": item.get("lndUse", "").strip(),
                "terrain": item.get("tpgrphHgCodeNm", "").strip(),
                "road_access": item.get("roadSideCodeNm", "").strip(),
            })
        return rows

    def get_sales_history(
        self,
        region_code: Optional[str] = None,
        start_year_month: Optional[str] = None,
        end_year_month: Optional[str] = None,
        land_category: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> pd.DataFrame:
        """Delegates to EventsClient.get_land_sales."""
        return self._events.get_land_sales(
            region_code=region_code,
            start_year_month=start_year_month,
            end_year_month=end_year_month,
            land_category=land_category,
            limit=limit,
        )

    # ------------------------------------------------------------------
    # Full profile
    # ------------------------------------------------------------------

    def get_full_profile(
        self,
        region_code: Optional[str] = None,
        parcel: Optional[str] = None,
        history_limit: int = 12,
        nearby_radius_m: Optional[int] = None,
    ) -> dict:
        """
        Unified land parcel profile combining zoning, appraised value, standard price,
        and recent sales history.

        Args:
            region_code: 5-digit 시군구 code.
            parcel: Jibun parcel number substring filter.
            history_limit: Months of sales history to include (default 12).
            nearby_radius_m: When set, include nearby parcel snapshots within this radius.
                             None = skip nearby enrichment.
        """
        region = region_code or config.DEFAULT_REGION_CODE
        cutoff = datetime.now() - relativedelta(months=history_limit)
        start_ym = cutoff.strftime("%Y%m")
        end_ym = datetime.now().strftime("%Y%m")

        zoning_df = self.get_zoning(region_code=region)
        appraised_df = self.get_appraised_value(region_code=region)
        standard_df = self.get_standard_price(region_code=region)
        sales_df = self._events.get_land_sales(
            region_code=region, start_year_month=start_ym, end_year_month=end_ym
        )

        if parcel:
            zoning_df = zoning_df[zoning_df["parcel"].str.contains(parcel, na=False)].reset_index(drop=True)
            appraised_df = appraised_df[appraised_df["parcel"].str.contains(parcel, na=False)].reset_index(drop=True)
            standard_df = standard_df[standard_df["parcel"].str.contains(parcel, na=False)].reset_index(drop=True)
            if not sales_df.empty:
                sales_df = sales_df[sales_df["parcel"].str.contains(parcel, na=False)].reset_index(drop=True)

        nearby = None
        if nearby_radius_m is not None:
            assert isinstance(nearby_radius_m, int) and nearby_radius_m > 0
            nearby = self._get_nearby_snapshots(region, parcel, nearby_radius_m)

        return {
            "parcel": {
                "zoning": zoning_df,
                "appraised_value": appraised_df,
                "standard_price": standard_df,
            },
            "history": {"sales": sales_df},
            "nearby": nearby,
        }

    def _get_nearby_snapshots(
        self,
        region_code: str,
        parcel: Optional[str],
        radius_m: int,
    ) -> list[dict]:
        # Spatial radius queries require a GIS backend not available in public APIs.
        # Returns empty list until a spatial index or cadastral proximity API is wired in.
        return []
