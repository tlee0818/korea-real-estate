"""MarketClient — regional market signals: price trends and commercial comps."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Optional

import pandas as pd
from dateutil.relativedelta import relativedelta

from .. import config
from ..http.reb import RebClient
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


def _apply_limit(df: pd.DataFrame, date_col: str, limit: Optional[int]) -> pd.DataFrame:
    if df.empty or limit is None:
        return df
    return df.sort_values(date_col, ascending=False).head(limit).reset_index(drop=True)


class MarketClient:
    """
    Regional market signals. Calls price trend API directly (REB).
    Delegates commercial sales history to EventsClient.
    """

    def __init__(
        self,
        events: Optional[EventsClient] = None,
        address: Optional[AddressClient] = None,
        http: Optional[RebClient] = None,
    ):
        self._http = http or RebClient()
        self._public = PublicDataClient()
        self._events = events or EventsClient(http=self._public)
        self._address = address or AddressClient()

    # ------------------------------------------------------------------
    # Individual methods
    # ------------------------------------------------------------------

    def get_price_trends(
        self,
        region_code: Optional[str] = None,
        index_type: str = "land",
        start_year_month: Optional[str] = None,
        end_year_month: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Land or housing price trend index (한국부동산원 통계 — REB).

        Args:
            region_code: 5-digit 시군구 code.
            index_type: "land" (지가변동률) or "housing" (주택가격동향).
            start_year_month: Start period (YYYYMM or YYYY-MM).
            end_year_month: End period (YYYYMM or YYYY-MM).
            limit: Return at most N most-recent rows. None = all.

        Returns: period, region, index_value, change_pct_mom, change_pct_yoy.
        """
        from ..utils.date_utils import to_year_month

        region = region_code or config.DEFAULT_REGION_CODE
        start = to_year_month(start_year_month) if start_year_month else None
        end = to_year_month(end_year_month) if end_year_month else None

        data = self._http.get_price_trends(
            region_code=region,
            index_type=index_type,
            start_year_month=start,
            end_year_month=end,
        )
        rows = self._parse_trends(data, region)
        df = pd.DataFrame(rows).sort_values("period").reset_index(drop=True)
        return _apply_limit(df, "period", limit)

    def _parse_trends(self, data: dict, region: str) -> list[dict]:
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

    def get_commercial_comps(
        self,
        region_code: Optional[str] = None,
        start_year_month: Optional[str] = None,
        end_year_month: Optional[str] = None,
        property_type: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> pd.DataFrame:
        """Delegates to EventsClient.get_commercial_sales."""
        return self._events.get_commercial_sales(
            region_code=region_code,
            start_year_month=start_year_month,
            end_year_month=end_year_month,
            property_type=property_type,
            limit=limit,
        )

    # ------------------------------------------------------------------
    # Full profile
    # ------------------------------------------------------------------

    def get_full_profile(
        self,
        region_code: Optional[str] = None,
        history_limit: int = 12,
        nearby_radius_m: Optional[int] = None,
    ) -> dict:
        """
        Combined market context: land + housing trends and recent commercial sales.

        Args:
            region_code: 5-digit 시군구 code.
            history_limit: Months of history to include (default 12).
            nearby_radius_m: When set, include market snapshot for nearby regions.
                             None = skip nearby enrichment.
        """
        region = region_code or config.DEFAULT_REGION_CODE
        cutoff = datetime.now() - relativedelta(months=history_limit)
        start_ym = cutoff.strftime("%Y%m")
        end_ym = datetime.now().strftime("%Y%m")

        land_trends = self.get_price_trends(region_code=region, index_type="land",
                                             start_year_month=start_ym, end_year_month=end_ym)
        housing_trends = self.get_price_trends(region_code=region, index_type="housing",
                                               start_year_month=start_ym, end_year_month=end_ym)
        commercial_sales = self._events.get_commercial_sales(
            region_code=region, start_year_month=start_ym, end_year_month=end_ym
        )

        nearby = None
        if nearby_radius_m is not None:
            assert isinstance(nearby_radius_m, int) and nearby_radius_m > 0
            nearby = self._get_nearby_snapshots(region, nearby_radius_m)

        return {
            "trends": {"land": land_trends, "housing": housing_trends},
            "history": {"commercial_sales": commercial_sales},
            "nearby": nearby,
        }

    def _get_nearby_snapshots(self, region_code: str, radius_m: int) -> list[dict]:
        # Spatial radius queries require a GIS backend not available in public APIs.
        return []
