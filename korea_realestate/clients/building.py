"""BuildingClient — building structure data: registry, GIS map layer, permit history."""

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


class BuildingClient:
    """
    Building structure data. Calls registry and GIS APIs directly.
    Delegates all permit history to EventsClient.
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

    def get_registry(
        self,
        region_code: Optional[str] = None,
        dong_code: Optional[str] = None,
        parcel_main: Optional[str] = None,
        parcel_sub: Optional[str] = None,
        ledger_type: str = "표제부",
        num_rows: int = 1000,
    ) -> pd.DataFrame:
        """
        Building ledger (건축물대장 — MOLIT).

        Args:
            region_code: 5-digit 시군구 code.
            dong_code: 읍면동 code.
            parcel_main: Main parcel number (본번).
            parcel_sub: Sub parcel number (부번). Default "0".
            ledger_type: 표제부 | 총괄표제부 | 층별개요 | 지역지구구역.
            num_rows: Max rows per API call.

        Returns: address, building_name, main_use, structure, floors_above, floors_below,
                 total_area_sqm, built_date, permit_date, approval_date, zoning.
        """
        region = region_code or config.DEFAULT_REGION_CODE
        data = self._http.get_building_registry(
            region_code=region,
            dong_code=dong_code,
            parcel_main=parcel_main,
            parcel_sub=parcel_sub,
            ledger_type=ledger_type,
            num_rows=num_rows,
        )
        rows = self._parse_registry(data)
        return pd.DataFrame(rows).reset_index(drop=True)

    def _parse_registry(self, data: dict) -> list[dict]:
        body = data.get("response", {}).get("body", {})
        raw_items = body.get("items", {}).get("item", [])
        if isinstance(raw_items, dict):
            raw_items = [raw_items]
        rows = []
        for item in raw_items:
            rows.append({
                "address": item.get("platPlc", "").strip(),
                "building_name": item.get("bldNm", "").strip() or None,
                "main_use": item.get("mainPurpsCdNm", "").strip(),
                "structure": item.get("strctCdNm", "").strip(),
                "floors_above": int(item["grndFlrCnt"]) if item.get("grndFlrCnt") else None,
                "floors_below": int(item["ugrndFlrCnt"]) if item.get("ugrndFlrCnt") else None,
                "total_area_sqm": float(_safe_decimal(item.get("totArea")) or 0),
                "built_date": item.get("useAprDay", "").strip() or None,
                "permit_date": item.get("pmsDay", "").strip() or None,
                "approval_date": item.get("archGbCdNm", "").strip() or None,
                "zoning": item.get("prposAreaDstrcNm", "").strip(),
            })
        return rows

    def get_map_layer(
        self,
        region_code: Optional[str] = None,
        bbox: Optional[tuple[float, float, float, float]] = None,
    ) -> dict:
        """
        Building footprints as GeoJSON FeatureCollection (GIS — MOLIT).

        Args:
            region_code: 5-digit 시군구 code.
            bbox: Optional (min_lon, min_lat, max_lon, max_lat) bounding box.

        Returns: GeoJSON FeatureCollection dict.
        """
        region = region_code or config.DEFAULT_REGION_CODE
        data = self._http.get_building_map(region_code=region, bbox=bbox)
        return self._parse_map_layer(data)

    def _parse_map_layer(self, data: dict) -> dict:
        # If the API returns GeoJSON directly
        if data.get("type") == "FeatureCollection":
            return data

        # Wrap flat item list in GeoJSON envelope
        body = data.get("response", {}).get("body", {})
        raw_items = body.get("items", {}).get("item", [])
        if isinstance(raw_items, dict):
            raw_items = [raw_items]

        features = []
        for item in raw_items:
            features.append({
                "type": "Feature",
                "geometry": None,  # geometry from GIS layer; absent in non-GeoJSON responses
                "properties": {
                    "address": item.get("platPlc", "").strip(),
                    "main_use": item.get("mainPurpsCdNm", "").strip(),
                    "floors": item.get("grndFlrCnt"),
                    "total_area_sqm": float(_safe_decimal(item.get("totArea")) or 0),
                    "built_year": (item.get("useAprDay", "") or "")[:4] or None,
                    "building_mgmt_no": item.get("mgmBldrgstPk", "").strip(),
                },
            })
        return {"type": "FeatureCollection", "features": features}

    def get_permit_history(
        self,
        region_code: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        permit_type: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> pd.DataFrame:
        """Delegates to EventsClient.get_permit_history."""
        return self._events.get_permit_history(
            region_code=region_code,
            start_date=start_date,
            end_date=end_date,
            permit_type=permit_type,
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
        Unified building profile combining registry, map layer, and recent permit history.

        Args:
            region_code: 5-digit 시군구 code.
            parcel: Jibun parcel number. Used to split into parcel_main/parcel_sub for registry.
            history_limit: Months of permit history to include (default 12).
            nearby_radius_m: When set, include nearby building snapshots within this radius.
                             None = skip nearby enrichment.
        """
        region = region_code or config.DEFAULT_REGION_CODE
        cutoff = datetime.now() - relativedelta(months=history_limit)

        parcel_main, parcel_sub = None, None
        if parcel:
            parts = parcel.replace("-", " ").split()
            parcel_main = parts[0] if parts else None
            parcel_sub = parts[1] if len(parts) > 1 else "0"

        registry_df = self.get_registry(
            region_code=region,
            parcel_main=parcel_main,
            parcel_sub=parcel_sub,
        )
        map_layer = self.get_map_layer(region_code=region)
        permits_df = self._events.get_permit_history(
            region_code=region,
            start_date=cutoff.strftime("%Y%m%d"),
        )

        nearby = None
        if nearby_radius_m is not None:
            assert isinstance(nearby_radius_m, int) and nearby_radius_m > 0
            nearby = self._get_nearby_snapshots(region, parcel, nearby_radius_m)

        return {
            "building": {
                "registry": registry_df,
                "map_layer": map_layer,
            },
            "history": {"permits": permits_df},
            "nearby": nearby,
        }

    def _get_nearby_snapshots(
        self,
        region_code: str,
        parcel: Optional[str],
        radius_m: int,
    ) -> list[dict]:
        # Spatial radius queries require a GIS backend not available in public APIs.
        return []
