"""HTTP client for https://apis.data.go.kr/ — one method per endpoint."""

from typing import Optional

from .. import config
from .base_http_client import BaseHttpClient

_BASE = "https://apis.data.go.kr/"

# Endpoint paths (relative to _BASE)
_LAND_SALES         = "1613000/RTMSDataSvcLandTrade/getRTMSDataSvcLandTrade"
_COMMERCIAL_SALES   = "1613000/RTMSDataSvcNrgTrade/getRTMSDataSvcNrgTrade"
_PERMIT_HISTORY     = "1613000/ArchPmsService/getApBasisOulnInfo"
_ZONING             = "1613000/LandUseService/getLandUseList"
_APPRAISED_VALUE    = "1611000/nsdi/IndvdLandPriceService/wfs/IndvdLandPrice"
_STANDARD_PRICE     = "1613000/PubLandPriceService/getPblcLandPriceList"
_BUILDING_REGISTRY  = "1613000/ArchPmsService/getApBdInfo"
_BUILDING_MAP       = "1613000/NSYDPnbldService/getNSYDPnbld"


def _p(**kwargs) -> dict:
    """Drop None values from params dict."""
    return {k: v for k, v in kwargs.items() if v is not None}


class PublicDataClient(BaseHttpClient):
    """
    All calls to apis.data.go.kr.
    Each public method maps 1:1 to a single API endpoint.
    Auth (serviceKey) and path are encapsulated here — callers pass domain params only.
    """

    def _call(self, path: str, api_key: str, params: dict) -> dict:
        return self._get(_BASE + path, {"serviceKey": api_key, **params})

    def _call_raw(self, path: str, params: dict) -> dict:
        """For endpoints that use a non-standard auth param (e.g. NSDI 'key')."""
        return self._get(_BASE + path, params)

    # ------------------------------------------------------------------
    # EventsClient endpoints
    # ------------------------------------------------------------------

    def get_land_sales(
        self,
        region_code: str,
        year_month: str,
        num_rows: int = 1000,
    ) -> dict:
        """토지 매매 실거래가 — one calendar month of land sale transactions."""
        return self._call(_LAND_SALES, config.SALES_HISTORY_API_KEY or "", _p(
            LAWD_CD=region_code,
            DEAL_YMD=year_month,
            numOfRows=num_rows,
            pageNo=1,
        ))

    def get_commercial_sales(
        self,
        region_code: str,
        year_month: str,
        num_rows: int = 1000,
    ) -> dict:
        """상업업무용·공장창고 매매 실거래가 — one month of commercial/warehouse sales."""
        return self._call(_COMMERCIAL_SALES, config.COMMERCIAL_SALES_API_KEY or "", _p(
            LAWD_CD=region_code,
            DEAL_YMD=year_month,
            numOfRows=num_rows,
            pageNo=1,
        ))

    def get_permit_history(
        self,
        region_code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        num_rows: int = 1000,
    ) -> dict:
        """건축인허가 기본개요 — building permit records for a region and date range."""
        return self._call(_PERMIT_HISTORY, config.BUILDING_PERMITS_API_KEY or "", _p(
            sigunguCd=region_code,
            startDate=start_date,
            endDate=end_date,
            numOfRows=num_rows,
            pageNo=1,
        ))

    # ------------------------------------------------------------------
    # LandClient endpoints
    # ------------------------------------------------------------------

    def get_zoning(
        self,
        region_code: str,
        dong: Optional[str] = None,
        num_rows: int = 1000,
    ) -> dict:
        """토지이용계획 — zoning and land-use classification for a region."""
        return self._call(_ZONING, config.ZONING_API_KEY or "", _p(
            pnu=region_code,
            umdNm=dong,
            numOfRows=num_rows,
            pageNo=1,
        ))

    def get_appraised_value(
        self,
        region_code: str,
        year: Optional[int] = None,
        num_rows: int = 1000,
    ) -> dict:
        """개별공시지가 — government-appraised land value (NSDI WFS; uses 'key' param)."""
        return self._call_raw(_APPRAISED_VALUE, _p(
            key=config.APPRAISED_VALUE_API_KEY,
            pnu=region_code,
            stdrYear=str(year) if year else None,
            numOfRows=num_rows,
            pageNo=1,
            format="json",
        ))

    def get_standard_price(
        self,
        region_code: str,
        year: Optional[int] = None,
        num_rows: int = 1000,
    ) -> dict:
        """표준지공시지가 — standard reference land price."""
        return self._call(_STANDARD_PRICE, config.STANDARD_LAND_PRICE_API_KEY or "", _p(
            sigunguCd=region_code,
            stdrYear=str(year) if year else None,
            numOfRows=num_rows,
            pageNo=1,
        ))

    # ------------------------------------------------------------------
    # BuildingClient endpoints
    # ------------------------------------------------------------------

    def get_building_registry(
        self,
        region_code: str,
        dong_code: Optional[str] = None,
        parcel_main: Optional[str] = None,
        parcel_sub: Optional[str] = None,
        ledger_type: str = "표제부",
        num_rows: int = 1000,
    ) -> dict:
        """건축물대장 — building ledger (registry) for a parcel."""
        return self._call(_BUILDING_REGISTRY, config.BUILDING_REGISTRY_API_KEY or "", _p(
            sigunguCd=region_code,
            bjdongCd=dong_code,
            platGbCd="0",
            bun=parcel_main,
            ji=parcel_sub or "0",
            ledgerType=ledger_type,
            numOfRows=num_rows,
            pageNo=1,
        ))

    def get_building_map(
        self,
        region_code: str,
        bbox: Optional[tuple[float, float, float, float]] = None,
        num_rows: int = 1000,
    ) -> dict:
        """GIS 건물 도면 — building footprints for a region, optionally clipped to bbox."""
        params: dict = _p(sigunguCd=region_code, numOfRows=num_rows, pageNo=1)
        if bbox:
            params["minX"], params["minY"], params["maxX"], params["maxY"] = bbox
        return self._call(_BUILDING_MAP, config.BUILDING_MAP_API_KEY or "", params)
