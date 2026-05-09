"""HTTP client for https://apis.data.go.kr/ — one method per endpoint."""

from .. import config
from .base_http_client import BaseHttpClient

_BASE = "https://apis.data.go.kr/"

_LAND_SALES = "1613000/RTMSDataSvcLandTrade/getRTMSDataSvcLandTrade"
_COMMERCIAL_SALES = "1613000/RTMSDataSvcNrgTrade/getRTMSDataSvcNrgTrade"
_PERMIT_HISTORY = "1613000/ArchPmsService/getApBasisOulnInfo"
_ZONING = "1613000/LandUseService/getLandUseList"
_APPRAISED_VALUE = "1611000/nsdi/IndvdLandPriceService/wfs/IndvdLandPrice"
_STANDARD_PRICE = "1613000/PubLandPriceService/getPblcLandPriceList"
_BUILDING_REGISTRY = "1613000/ArchPmsService/getApBdInfo"
_BUILDING_MAP = "1613000/NSYDPnbldService/getNSYDPnbld"


def _p(**kwargs) -> dict:
    return {k: v for k, v in kwargs.items() if v is not None}


class PublicDataClient(BaseHttpClient):
    """
    All calls to apis.data.go.kr.
    Each method maps 1:1 to one API endpoint and returns the raw parsed dict.
    Auth (serviceKey) is injected here — callers pass domain params only.
    """

    def _call(self, path: str, api_key: str, params: dict) -> dict:
        return self._get(_BASE + path, {"serviceKey": api_key, **params})

    def _call_raw(self, path: str, params: dict) -> dict:
        """For endpoints that use a non-standard auth param (e.g. NSDI 'key')."""
        return self._get(_BASE + path, params)

    def land_trade_history(
        self,
        region_code: str,
        year_month: str,
        num_rows: int = 1000,
    ) -> dict:
        """토지 매매 실거래가 — land sale transactions for one calendar month."""
        return self._call(
            _LAND_SALES,
            config.PUBLIC_DATA_API_KEY or "",
            _p(
                LAWD_CD=region_code,
                DEAL_YMD=year_month,
                numOfRows=num_rows,
                pageNo=1,
            ),
        )

    def commercial_trade_history(
        self,
        region_code: str,
        year_month: str,
        num_rows: int = 1000,
    ) -> dict:
        """상업업무용·공장창고 매매 실거래가 — commercial/warehouse sales for one month."""
        return self._call(
            _COMMERCIAL_SALES,
            config.PUBLIC_DATA_API_KEY or "",
            _p(
                LAWD_CD=region_code,
                DEAL_YMD=year_month,
                numOfRows=num_rows,
                pageNo=1,
            ),
        )

    def building_permit_records(
        self,
        region_code: str,
        start_date: str | None = None,
        end_date: str | None = None,
        num_rows: int = 1000,
    ) -> dict:
        """건축인허가 기본개요 — building permit records for a region and date range."""
        return self._call(
            _PERMIT_HISTORY,
            config.PUBLIC_DATA_API_KEY or "",
            _p(
                sigunguCd=region_code,
                startDate=start_date,
                endDate=end_date,
                numOfRows=num_rows,
                pageNo=1,
            ),
        )

    def land_use_zoning(
        self,
        region_code: str,
        dong: str | None = None,
        num_rows: int = 1000,
    ) -> dict:
        """토지이용계획 — zoning and land-use classification for a region."""
        return self._call(
            _ZONING,
            config.PUBLIC_DATA_API_KEY or "",
            _p(
                pnu=region_code,
                umdNm=dong,
                numOfRows=num_rows,
                pageNo=1,
            ),
        )

    def individual_land_price(
        self,
        region_code: str,
        year: int | None = None,
        num_rows: int = 1000,
    ) -> dict:
        """개별공시지가 — government-appraised individual land price (NSDI; uses 'key' param)."""
        return self._call_raw(
            _APPRAISED_VALUE,
            _p(
                key=config.NSDI_API_KEY,
                pnu=region_code,
                stdrYear=str(year) if year else None,
                numOfRows=num_rows,
                pageNo=1,
                format="json",
            ),
        )

    def standard_land_price(
        self,
        region_code: str,
        year: int | None = None,
        num_rows: int = 1000,
    ) -> dict:
        """표준지공시지가 — publicly announced standard land price."""
        return self._call(
            _STANDARD_PRICE,
            config.PUBLIC_DATA_API_KEY or "",
            _p(
                sigunguCd=region_code,
                stdrYear=str(year) if year else None,
                numOfRows=num_rows,
                pageNo=1,
            ),
        )

    def building_ledger(
        self,
        region_code: str,
        dong_code: str | None = None,
        parcel_main: str | None = None,
        parcel_sub: str | None = None,
        ledger_type: str = "표제부",
        num_rows: int = 1000,
    ) -> dict:
        """건축물대장 — building ledger for a parcel."""
        return self._call(
            _BUILDING_REGISTRY,
            config.PUBLIC_DATA_API_KEY or "",
            _p(
                sigunguCd=region_code,
                bjdongCd=dong_code,
                platGbCd="0",
                bun=parcel_main,
                ji=parcel_sub or "0",
                ledgerType=ledger_type,
                numOfRows=num_rows,
                pageNo=1,
            ),
        )

    def building_spatial_info(
        self,
        region_code: str,
        bbox: tuple[float, float, float, float] | None = None,
        num_rows: int = 1000,
    ) -> dict:
        """GIS 건물 도면 — building footprints for a region, optionally clipped to bbox."""
        params: dict = _p(sigunguCd=region_code, numOfRows=num_rows, pageNo=1)
        if bbox:
            params["minX"], params["minY"], params["maxX"], params["maxY"] = bbox
        return self._call(_BUILDING_MAP, config.PUBLIC_DATA_API_KEY or "", params)

    # -------------------------------------------------------------------------
    # SECTION: Apartment Transaction Data
    # -------------------------------------------------------------------------

    _APT_TRADE = "1613000/RTMSDataSvcAptTrade/getRTMSDataSvcAptTrade"
    _APT_TRADE_DEV = "1613000/RTMSDataSvcAptTradeDev/getRTMSDataSvcAptTradeDev"
    _APT_RENT = "1613000/RTMSDataSvcAptRent/getRTMSDataSvcAptRent"
    _OFFI_TRADE = "1613000/RTMSDataSvcOffiTrade/getRTMSDataSvcOffiTrade"
    _OFFI_RENT = "1613000/RTMSDataSvcOffiRent/getRTMSDataSvcOffiRent"
    _RH_TRADE = "1613000/RTMSDataSvcRHTrade/getRTMSDataSvcRHTrade"
    _RH_RENT = "1613000/RTMSDataSvcRHRent/getRTMSDataSvcRHRent"
    _SH_TRADE = "1613000/RTMSDataSvcSHTrade/getRTMSDataSvcSHTrade"
    _SH_RENT = "1613000/RTMSDataSvcSHRent/getRTMSDataSvcSHRent"
    _APT_PRESALE = "1613000/RTMSDataSvcSilvTrade/getRTMSDataSvcSilvTrade"
    _INDU_TRADE = "1613000/RTMSDataSvcInduTrade/getRTMSDataSvcInduTrade"

    def apartment_trade_history(
        self,
        region_code: str,
        year_month: str,
        num_rows: int = 1000,
    ) -> dict:
        """아파트 매매 실거래가 — apartment sale transactions for one month."""
        return self._call(
            self._APT_TRADE,
            config.PUBLIC_DATA_API_KEY or "",
            _p(LAWD_CD=region_code, DEAL_YMD=year_month, numOfRows=num_rows, pageNo=1),
        )

    def apartment_trade_history_detailed(
        self,
        region_code: str,
        year_month: str,
        num_rows: int = 1000,
    ) -> dict:
        """아파트 매매 실거래가 상세 — detailed apartment sale transactions including floor/area breakdown."""
        return self._call(
            self._APT_TRADE_DEV,
            config.PUBLIC_DATA_API_KEY or "",
            _p(LAWD_CD=region_code, DEAL_YMD=year_month, numOfRows=num_rows, pageNo=1),
        )

    def apartment_rent_history(
        self,
        region_code: str,
        year_month: str,
        num_rows: int = 1000,
    ) -> dict:
        """아파트 전월세 실거래가 — apartment lease/jeonse transactions for one month."""
        return self._call(
            self._APT_RENT,
            config.PUBLIC_DATA_API_KEY or "",
            _p(LAWD_CD=region_code, DEAL_YMD=year_month, numOfRows=num_rows, pageNo=1),
        )

    def officetel_trade_history(
        self,
        region_code: str,
        year_month: str,
        num_rows: int = 1000,
    ) -> dict:
        """오피스텔 매매 실거래가 — officetel sale transactions for one month."""
        return self._call(
            self._OFFI_TRADE,
            config.PUBLIC_DATA_API_KEY or "",
            _p(LAWD_CD=region_code, DEAL_YMD=year_month, numOfRows=num_rows, pageNo=1),
        )

    def officetel_rent_history(
        self,
        region_code: str,
        year_month: str,
        num_rows: int = 1000,
    ) -> dict:
        """오피스텔 전월세 실거래가 — officetel lease/jeonse transactions for one month."""
        return self._call(
            self._OFFI_RENT,
            config.PUBLIC_DATA_API_KEY or "",
            _p(LAWD_CD=region_code, DEAL_YMD=year_month, numOfRows=num_rows, pageNo=1),
        )

    def rowhouse_multiplex_trade_history(
        self,
        region_code: str,
        year_month: str,
        num_rows: int = 1000,
    ) -> dict:
        """연립다세대 매매 실거래가 — rowhouse and multi-family dwelling sale transactions."""
        return self._call(
            self._RH_TRADE,
            config.PUBLIC_DATA_API_KEY or "",
            _p(LAWD_CD=region_code, DEAL_YMD=year_month, numOfRows=num_rows, pageNo=1),
        )

    def rowhouse_multiplex_rent_history(
        self,
        region_code: str,
        year_month: str,
        num_rows: int = 1000,
    ) -> dict:
        """연립다세대 전월세 실거래가 — rowhouse and multi-family dwelling lease transactions."""
        return self._call(
            self._RH_RENT,
            config.PUBLIC_DATA_API_KEY or "",
            _p(LAWD_CD=region_code, DEAL_YMD=year_month, numOfRows=num_rows, pageNo=1),
        )

    def detached_house_trade_history(
        self,
        region_code: str,
        year_month: str,
        num_rows: int = 1000,
    ) -> dict:
        """단독/다가구 매매 실거래가 — detached and multi-unit house sale transactions."""
        return self._call(
            self._SH_TRADE,
            config.PUBLIC_DATA_API_KEY or "",
            _p(LAWD_CD=region_code, DEAL_YMD=year_month, numOfRows=num_rows, pageNo=1),
        )

    def detached_house_rent_history(
        self,
        region_code: str,
        year_month: str,
        num_rows: int = 1000,
    ) -> dict:
        """단독/다가구 전월세 실거래가 — detached and multi-unit house lease transactions."""
        return self._call(
            self._SH_RENT,
            config.PUBLIC_DATA_API_KEY or "",
            _p(LAWD_CD=region_code, DEAL_YMD=year_month, numOfRows=num_rows, pageNo=1),
        )

    def apartment_presale_rights_trade_history(
        self,
        region_code: str,
        year_month: str,
        num_rows: int = 1000,
    ) -> dict:
        """아파트 분양권전매 실거래가 — apartment pre-sale rights transfer transactions."""
        return self._call(
            self._APT_PRESALE,
            config.PUBLIC_DATA_API_KEY or "",
            _p(LAWD_CD=region_code, DEAL_YMD=year_month, numOfRows=num_rows, pageNo=1),
        )

    def industrial_warehouse_factory_trade_history(
        self,
        region_code: str,
        year_month: str,
        num_rows: int = 1000,
    ) -> dict:
        """공장 및 창고 등 부동산 매매 실거래가 — industrial, warehouse, and factory property sale transactions."""
        return self._call(
            self._INDU_TRADE,
            config.PUBLIC_DATA_API_KEY or "",
            _p(LAWD_CD=region_code, DEAL_YMD=year_month, numOfRows=num_rows, pageNo=1),
        )

    # -------------------------------------------------------------------------
    # SECTION: REITs (Real Estate Investment Trusts)
    # -------------------------------------------------------------------------

    _REITS_COMPANY_LIST = "1613000/ReitsService/ReitsInfo/getReitsCmpnyList"
    _REITS_INVEST_TARGETS = "1613000/ReitsService/ReitsInfo/getReitsInvtTrgtList"
    _REITS_ANNOUNCEMENTS = "1613000/ReitsService/ReitsInfo/getReitsPblntfList"
    _REITS_FUNDRAISING = "1613000/ReitsService/ReitsInfo/getReitsPssrpList"
    _REITS_AMC_COMPANIES = "1613000/ReitsService/AmcInfo/getAmcCmpnyList"
    _REITS_AMC_CONTRACTS = "1613000/ReitsService/AmcInfo/getAmcJobCnsgnList"
    _REITS_AMC_NOTICES = "1613000/ReitsService/AmcInfo/getAmcPblntfList"
    _REITS_AMC_FUNDRAISING = "1613000/ReitsService/AmcInfo/getAmcPssrpList"

    def reits_company_list(self, num_rows: int = 100, page: int = 1, **kwargs) -> dict:
        """부동산투자회사(리츠) 정보 — list of registered REITs companies with approval status and AMC."""
        return self._call(
            self._REITS_COMPANY_LIST,
            config.PUBLIC_DATA_API_KEY or "",
            _p(
                numOfRows=num_rows,
                pageNo=page,
                **{k: v for k, v in kwargs.items() if v is not None},
            ),
        )

    def reits_investment_targets(self, num_rows: int = 100, page: int = 1, **kwargs) -> dict:
        """리츠 투자대상 목록 — investment target assets held by REITs companies."""
        return self._call(
            self._REITS_INVEST_TARGETS,
            config.PUBLIC_DATA_API_KEY or "",
            _p(
                numOfRows=num_rows,
                pageNo=page,
                **{k: v for k, v in kwargs.items() if v is not None},
            ),
        )

    def reits_announcements(self, num_rows: int = 100, page: int = 1, **kwargs) -> dict:
        """리츠 공시 목록 — REITs regulatory announcements and disclosures."""
        return self._call(
            self._REITS_ANNOUNCEMENTS,
            config.PUBLIC_DATA_API_KEY or "",
            _p(
                numOfRows=num_rows,
                pageNo=page,
                **{k: v for k, v in kwargs.items() if v is not None},
            ),
        )

    def reits_fundraising_list(self, num_rows: int = 100, page: int = 1, **kwargs) -> dict:
        """리츠 모집·매출 목록 — REITs fundraising and share offering records."""
        return self._call(
            self._REITS_FUNDRAISING,
            config.PUBLIC_DATA_API_KEY or "",
            _p(
                numOfRows=num_rows,
                pageNo=page,
                **{k: v for k, v in kwargs.items() if v is not None},
            ),
        )

    def reits_amc_company_list(self, num_rows: int = 100, page: int = 1, **kwargs) -> dict:
        """자산관리회사(AMC) 정보 — list of registered REITs asset management companies."""
        return self._call(
            self._REITS_AMC_COMPANIES,
            config.PUBLIC_DATA_API_KEY or "",
            _p(
                numOfRows=num_rows,
                pageNo=page,
                **{k: v for k, v in kwargs.items() if v is not None},
            ),
        )

    def reits_amc_consignment_contracts(self, num_rows: int = 100, page: int = 1, **kwargs) -> dict:
        """AMC 업무수탁 목록 — AMC consignment and management contract records."""
        return self._call(
            self._REITS_AMC_CONTRACTS,
            config.PUBLIC_DATA_API_KEY or "",
            _p(
                numOfRows=num_rows,
                pageNo=page,
                **{k: v for k, v in kwargs.items() if v is not None},
            ),
        )

    def reits_amc_announcements(self, num_rows: int = 100, page: int = 1, **kwargs) -> dict:
        """AMC 공시 목록 — AMC regulatory announcements and disclosures."""
        return self._call(
            self._REITS_AMC_NOTICES,
            config.PUBLIC_DATA_API_KEY or "",
            _p(
                numOfRows=num_rows,
                pageNo=page,
                **{k: v for k, v in kwargs.items() if v is not None},
            ),
        )

    def reits_amc_fundraising_list(self, num_rows: int = 100, page: int = 1, **kwargs) -> dict:
        """AMC 모집·매출 목록 — AMC fundraising and share offering records."""
        return self._call(
            self._REITS_AMC_FUNDRAISING,
            config.PUBLIC_DATA_API_KEY or "",
            _p(
                numOfRows=num_rows,
                pageNo=page,
                **{k: v for k, v in kwargs.items() if v is not None},
            ),
        )

    # -------------------------------------------------------------------------
    # SECTION: KAMCO Onbid — Public Auction (온비드)
    # -------------------------------------------------------------------------

    _ONBID_PROPERTY_DETAIL = "B010003/OnbidRlstDtlSrvc2/getRlstDtlInf2"
    _ONBID_PROPERTY_LIST = "B010003/OnbidRlstListSrvc2/getRlstCltrList2"
    _ONBID_INTEREST_RANK = "B010003/OnbidItrsCltrRnkClgSrvc/getItrsCltrRnkClg"
    _ONBID_VIEW_COUNT_RANK = "B010003/OnbidInqRnkClgSrvc/getInqRnkClg"
    _ONBID_HIGH_MARKDOWN_RANK = "B010003/Onbid50PctDecrCltrSrvc/get50PctDecrCltr"
    _ONBID_ANNOUNCE_PROPERTY = "B010003/OnbidPbancCltrDtlSrvc2/getPbancCltrInf2"
    _ONBID_BID_RESULT_DETAIL = "B010003/OnbidCltrBidRsltDtlSrvc2/getCltrBidRsltDtl2"
    _ONBID_ANNOUNCE_BID_RESULTS = "B010003/OnbidPbancBidRsltListSrvc2/getPbancBidRsltList2"
    _ONBID_ANNOUNCE_DETAIL = "B010003/OnbidPbancDtlnfSrvc2/getPbancDtlInf2"
    _ONBID_KAMCO_REGIONAL_STATS = "B010003/OnbidClarBidStatsSrvc/getKamcoCltrClarStats"
    _ONBID_ORG_REGIONAL_STATS = "B010003/OnbidClarBidStatsSrvc/getOrgCltrClarStats"
    _ONBID_KAMCO_TYPE_STATS = "B010003/OnbidUsgBidStatsSrvc/getKamcoCltrUsgStats"
    _ONBID_ORG_TYPE_STATS = "B010003/OnbidUsgBidStatsSrvc/getOrgCltrUsgStats"
    _ONBID_PROPERTY_BID_INFO = "B010003/OnbidCltrBidDtlSrvc2/getCltrBidInf2"

    def onbid_property_detail(
        self,
        property_id: str,
        auction_condition_no: str | None = None,
        **kwargs,
    ) -> dict:
        """온비드 부동산 물건상세 조회 — detailed Onbid property listing by property management number."""
        return self._call(
            self._ONBID_PROPERTY_DETAIL,
            config.PUBLIC_DATA_API_KEY or "",
            _p(cltrMngNo=property_id, pbctCdtnNo=auction_condition_no, **kwargs),
        )

    def onbid_property_listing(self, num_rows: int = 100, page: int = 1, **kwargs) -> dict:
        """온비드 부동산 물건목록 조회 — list of real estate properties currently listed on Onbid public auction platform."""
        return self._call(
            self._ONBID_PROPERTY_LIST,
            config.PUBLIC_DATA_API_KEY or "",
            _p(
                numOfRows=num_rows,
                pageNo=page,
                **{k: v for k, v in kwargs.items() if v is not None},
            ),
        )

    def onbid_interest_rank(self, num_rows: int = 100, page: int = 1, **kwargs) -> dict:
        """온비드 관심물건 순위 — properties ranked by number of user interest/bookmarks on Onbid."""
        return self._call(
            self._ONBID_INTEREST_RANK,
            config.PUBLIC_DATA_API_KEY or "",
            _p(
                numOfRows=num_rows,
                pageNo=page,
                **{k: v for k, v in kwargs.items() if v is not None},
            ),
        )

    def onbid_view_count_rank(self, num_rows: int = 100, page: int = 1, **kwargs) -> dict:
        """온비드 조회수 순위 — properties ranked by page view count on Onbid."""
        return self._call(
            self._ONBID_VIEW_COUNT_RANK,
            config.PUBLIC_DATA_API_KEY or "",
            _p(
                numOfRows=num_rows,
                pageNo=page,
                **{k: v for k, v in kwargs.items() if v is not None},
            ),
        )

    def onbid_high_markdown_rank(self, num_rows: int = 100, page: int = 1, **kwargs) -> dict:
        """온비드 저감률 순위 — properties with highest price reductions (50%+ markdown) on Onbid."""
        return self._call(
            self._ONBID_HIGH_MARKDOWN_RANK,
            config.PUBLIC_DATA_API_KEY or "",
            _p(
                numOfRows=num_rows,
                pageNo=page,
                **{k: v for k, v in kwargs.items() if v is not None},
            ),
        )

    def onbid_announcement_property_info(
        self, num_rows: int = 100, page: int = 1, **kwargs
    ) -> dict:
        """온비드 공고상세 물건정보 조회 — property details within a specific Onbid auction announcement."""
        return self._call(
            self._ONBID_ANNOUNCE_PROPERTY,
            config.PUBLIC_DATA_API_KEY or "",
            _p(
                numOfRows=num_rows,
                pageNo=page,
                **{k: v for k, v in kwargs.items() if v is not None},
            ),
        )

    def onbid_bid_result_detail(
        self,
        property_id: str | None = None,
        num_rows: int = 100,
        page: int = 1,
        **kwargs,
    ) -> dict:
        """온비드 물건 입찰결과상세 조회 — detailed bid result for a specific Onbid property."""
        return self._call(
            self._ONBID_BID_RESULT_DETAIL,
            config.PUBLIC_DATA_API_KEY or "",
            _p(
                cltrMngNo=property_id,
                numOfRows=num_rows,
                pageNo=page,
                **{k: v for k, v in kwargs.items() if v is not None},
            ),
        )

    def onbid_announcement_bid_results(self, num_rows: int = 100, page: int = 1, **kwargs) -> dict:
        """온비드 공고 입찰결과목록 조회 — list of bid results for all properties in an Onbid announcement."""
        return self._call(
            self._ONBID_ANNOUNCE_BID_RESULTS,
            config.PUBLIC_DATA_API_KEY or "",
            _p(
                numOfRows=num_rows,
                pageNo=page,
                **{k: v for k, v in kwargs.items() if v is not None},
            ),
        )

    def onbid_announcement_detail(self, num_rows: int = 100, page: int = 1, **kwargs) -> dict:
        """온비드 공고상세 조회 — full details of an Onbid auction announcement."""
        return self._call(
            self._ONBID_ANNOUNCE_DETAIL,
            config.PUBLIC_DATA_API_KEY or "",
            _p(
                numOfRows=num_rows,
                pageNo=page,
                **{k: v for k, v in kwargs.items() if v is not None},
            ),
        )

    def onbid_kamco_regional_bid_stats(self, num_rows: int = 100, page: int = 1, **kwargs) -> dict:
        """온비드 KAMCO 지역별 입찰통계 — KAMCO-managed property auction bid statistics by region."""
        return self._call(
            self._ONBID_KAMCO_REGIONAL_STATS,
            config.PUBLIC_DATA_API_KEY or "",
            _p(
                numOfRows=num_rows,
                pageNo=page,
                **{k: v for k, v in kwargs.items() if v is not None},
            ),
        )

    def onbid_org_regional_bid_stats(self, num_rows: int = 100, page: int = 1, **kwargs) -> dict:
        """온비드 기관별 지역별 입찰통계 — organization-level regional bid statistics on Onbid."""
        return self._call(
            self._ONBID_ORG_REGIONAL_STATS,
            config.PUBLIC_DATA_API_KEY or "",
            _p(
                numOfRows=num_rows,
                pageNo=page,
                **{k: v for k, v in kwargs.items() if v is not None},
            ),
        )

    def onbid_kamco_property_type_bid_stats(
        self, num_rows: int = 100, page: int = 1, **kwargs
    ) -> dict:
        """온비드 KAMCO 용도별 입찰통계 — KAMCO-managed property auction bid statistics by property type."""
        return self._call(
            self._ONBID_KAMCO_TYPE_STATS,
            config.PUBLIC_DATA_API_KEY or "",
            _p(
                numOfRows=num_rows,
                pageNo=page,
                **{k: v for k, v in kwargs.items() if v is not None},
            ),
        )

    def onbid_org_property_type_bid_stats(
        self, num_rows: int = 100, page: int = 1, **kwargs
    ) -> dict:
        """온비드 기관별 용도별 입찰통계 — organization-level property type bid statistics on Onbid."""
        return self._call(
            self._ONBID_ORG_TYPE_STATS,
            config.PUBLIC_DATA_API_KEY or "",
            _p(
                numOfRows=num_rows,
                pageNo=page,
                **{k: v for k, v in kwargs.items() if v is not None},
            ),
        )

    def onbid_property_bid_info(self, num_rows: int = 100, page: int = 1, **kwargs) -> dict:
        """온비드 물건상세 입찰정보 조회 — bid schedule and conditions for a specific Onbid listed property."""
        return self._call(
            self._ONBID_PROPERTY_BID_INFO,
            config.PUBLIC_DATA_API_KEY or "",
            _p(
                numOfRows=num_rows,
                pageNo=page,
                **{k: v for k, v in kwargs.items() if v is not None},
            ),
        )

    # -------------------------------------------------------------------------
    # SECTION: KAMCO Government Property Management
    # -------------------------------------------------------------------------

    _KAMCO_RELOCATION_PROPERTY = "B010003/kamcoRlctRlst/pscd"
    _KAMCO_RESERVE_INVENTORY = "B010003/kamcoRlgStmn/stmnPscd"
    _KAMCO_VACANCY_INFO = "B010003/pblcDvlpRlst/ophsInf"
    _KAMCO_FACILITY_STATUS = "B010003/pblcDvlpRlstFclt/fcltInf"
    _KAMCO_INTEREST_RATES = "B010003/kamcoRliItrtMng"
    _KAMCO_APPRAISAL_AGENCIES = "B010003/kamcoRliApslOrg"
    _NATIONAL_PROPERTY_SALES = "B010003/kamcoGvwsRlstDsplPscd/dsplPscdInqSrvc"
    _NATIONAL_PROPERTY_LEASE = "B010003/GvwsRlstRent"
    _SEIZED_PROPERTY_WIN_RATE = "B010003/szrPrptPbctPbct"
    _ENTRUSTED_NONBIZ_SALES = "B010003/kamcoTrstNbppDspl"

    def kamco_relocation_property_status(
        self, num_rows: int = 100, page: int = 1, **kwargs
    ) -> dict:
        """종전부동산 관련 현황 — status of former residential properties managed by KAMCO for relocation housing programs."""
        return self._call(
            self._KAMCO_RELOCATION_PROPERTY,
            config.PUBLIC_DATA_API_KEY or "",
            _p(
                numOfRows=num_rows,
                pageNo=page,
                **{k: v for k, v in kwargs.items() if v is not None},
            ),
        )

    def kamco_reserve_property_inventory(
        self, num_rows: int = 100, page: int = 1, **kwargs
    ) -> dict:
        """비축부동산 명세 현황 — inventory of reserve real estate held by KAMCO for public housing supply purposes."""
        return self._call(
            self._KAMCO_RESERVE_INVENTORY,
            config.PUBLIC_DATA_API_KEY or "",
            _p(
                numOfRows=num_rows,
                pageNo=page,
                **{k: v for k, v in kwargs.items() if v is not None},
            ),
        )

    def public_development_property_vacancy(
        self, num_rows: int = 100, page: int = 1, **kwargs
    ) -> dict:
        """공공개발부동산 공실정보 — vacancy information for publicly developed commercial/residential properties managed by KAMCO."""
        return self._call(
            self._KAMCO_VACANCY_INFO,
            config.PUBLIC_DATA_API_KEY or "",
            _p(
                numOfRows=num_rows,
                pageNo=page,
                **{k: v for k, v in kwargs.items() if v is not None},
            ),
        )

    def public_development_property_facilities(
        self, num_rows: int = 100, page: int = 1, **kwargs
    ) -> dict:
        """공공개발부동산 시설현황 — facility status and details for publicly developed properties managed by KAMCO."""
        return self._call(
            self._KAMCO_FACILITY_STATUS,
            config.PUBLIC_DATA_API_KEY or "",
            _p(
                numOfRows=num_rows,
                pageNo=page,
                **{k: v for k, v in kwargs.items() if v is not None},
            ),
        )

    def kamco_interest_rate_schedule(self, num_rows: int = 100, page: int = 1, **kwargs) -> dict:
        """부동산공통 이율관리내역 — interest rate schedules applied to KAMCO-managed real estate transactions."""
        return self._call(
            self._KAMCO_INTEREST_RATES,
            config.PUBLIC_DATA_API_KEY or "",
            _p(
                numOfRows=num_rows,
                pageNo=page,
                **{k: v for k, v in kwargs.items() if v is not None},
            ),
        )

    def kamco_appraisal_agency_registry(self, num_rows: int = 100, page: int = 1, **kwargs) -> dict:
        """부동산공통 감정기관정보 — registry of certified real estate appraisal agencies recognized by KAMCO."""
        return self._call(
            self._KAMCO_APPRAISAL_AGENCIES,
            config.PUBLIC_DATA_API_KEY or "",
            _p(
                numOfRows=num_rows,
                pageNo=page,
                **{k: v for k, v in kwargs.items() if v is not None},
            ),
        )

    def national_property_sales_status(self, num_rows: int = 100, page: int = 1, **kwargs) -> dict:
        """국유부동산 매각현황 — sales status of national government-owned real estate."""
        return self._call(
            self._NATIONAL_PROPERTY_SALES,
            config.PUBLIC_DATA_API_KEY or "",
            _p(
                numOfRows=num_rows,
                pageNo=page,
                **{k: v for k, v in kwargs.items() if v is not None},
            ),
        )

    def national_property_lease_status(self, num_rows: int = 100, page: int = 1, **kwargs) -> dict:
        """국유부동산 임대현황 — lease status of national government-owned real estate."""
        return self._call(
            self._NATIONAL_PROPERTY_LEASE,
            config.PUBLIC_DATA_API_KEY or "",
            _p(
                numOfRows=num_rows,
                pageNo=page,
                **{k: v for k, v in kwargs.items() if v is not None},
            ),
        )

    def seized_property_auction_win_rate(
        self, num_rows: int = 100, page: int = 1, **kwargs
    ) -> dict:
        """체납 압류재산 공매 낙찰가율 — bid success rate and winning price ratios for seized delinquent taxpayer property auctions."""
        return self._call(
            self._SEIZED_PROPERTY_WIN_RATE,
            config.PUBLIC_DATA_API_KEY or "",
            _p(
                numOfRows=num_rows,
                pageNo=page,
                **{k: v for k, v in kwargs.items() if v is not None},
            ),
        )

    def entrusted_nonbusiness_property_sales(
        self, num_rows: int = 100, page: int = 1, **kwargs
    ) -> dict:
        """수탁 비업무용 자산 매각정보 — sales information for non-business assets entrusted to KAMCO for disposal."""
        return self._call(
            self._ENTRUSTED_NONBIZ_SALES,
            config.PUBLIC_DATA_API_KEY or "",
            _p(
                numOfRows=num_rows,
                pageNo=page,
                **{k: v for k, v in kwargs.items() if v is not None},
            ),
        )

    # -------------------------------------------------------------------------
    # SECTION: Transportation Route Data
    # -------------------------------------------------------------------------

    _TRANSPORT_ROUTE_BASE = "1613000/MostFrequentTransportationRouteData"
    _TRANSPORT_CITY_PATHS = {
        "seoul": "Seoul",
        "incheon": "Incheon",
        "gyeonggi": "Gyeonggi",
        "busan": "Busan",
        "daegu": "Daegu",
        "gwangju": "Gwangju",
        "daejeon": "Daejeon",
        "ulsan": "Ulsan",
        "jeju": "Jeju",
    }

    def most_frequent_transit_routes(
        self,
        city: str,
        period: str = "monthly",
        num_rows: int = 1000,
    ) -> dict:
        """
        최빈교통이용 경로 데이터 — most frequently used transit routes between origin-destination
        pairs for a given city, aggregated monthly or yearly.

        Args:
            city: One of: seoul, incheon, gyeonggi, busan, daegu, gwangju, daejeon, ulsan, jeju.
            period: "monthly" or "yearly".
            num_rows: Max rows to return.
        """
        city_key = city.lower()
        if city_key not in self._TRANSPORT_CITY_PATHS:
            raise ValueError(
                f"city must be one of {list(self._TRANSPORT_CITY_PATHS)}, got {city!r}"
            )
        if period not in ("monthly", "yearly"):
            raise ValueError(f"period must be 'monthly' or 'yearly', got {period!r}")
        period_suffix = "Monthly" if period == "monthly" else "Yearly"
        city_name = self._TRANSPORT_CITY_PATHS[city_key]
        path = f"{self._TRANSPORT_ROUTE_BASE}/get{city_name}MostFrequentTransportationRouteData{period_suffix}"
        return self._call(path, config.PUBLIC_DATA_API_KEY or "", _p(numOfRows=num_rows, pageNo=1))

    # -------------------------------------------------------------------------
    # SECTION: Regional Government APIs
    # -------------------------------------------------------------------------

    _YEONGCHEON_BROKERS = "5100000/YeongcheonRealestate/getResult"
    _DAEGU_DONGGU_BROKERS = "3420000/openBrokerageService/getOpenBrokerage"
    _DAEGU_DONGGU_APARTMENTS = "3420000/apartmentsManagementService/getApartmentsManagement"
    _DAEGU_DONGGU_MAINTENANCE = (
        "3420000/maintenanceProjectStatusService/getMaintenanceProjectStatus"
    )
    _YEONGDEOK_HOUSE_PRICE = "6470000/YeongdeokHousePrice"
    _SANGJU_BUILDING_VALUE = "5110000/propertyValue"
    _YEONGJU_LAND_PROPERTY = "5090000/landPropertyService/getLandProperty"
    _YEONGJU_USE_DISTRICT = "5090000/useDistrictService/getUseDistrict"
    _YEONGJU_DEV_PERMITS = "5090000/developmentPermissionService/getPermissionService"
    _YEONGJU_FOREST_CONVERSION = "5090000/exclusivePermissionService/getExclusivePermissionService"
    _YEONGJU_FARMLAND_CONVERSION = "5090000/farmlandOnlyService/getFarmlandOnlyService"
    _YEONGJU_LOCAL_TAX_ARREARS = "5090000/localTaxArrearsService/getLocalTaxArrearsService"

    def yeongcheon_real_estate_brokers(self, num_rows: int = 1000, page: int = 1, **kwargs) -> dict:
        """경상북도 영천시 부동산중개업 현황 — licensed real estate brokers registered in Yeongcheon, North Gyeongsang Province."""
        return self._call(
            self._YEONGCHEON_BROKERS,
            config.PUBLIC_DATA_API_KEY or "",
            _p(
                numOfRows=num_rows,
                pageNo=page,
                **{k: v for k, v in kwargs.items() if v is not None},
            ),
        )

    def daegu_donggu_real_estate_brokers(
        self, num_rows: int = 1000, page: int = 1, **kwargs
    ) -> dict:
        """대구광역시 동구 개업공인중개사 현황 — licensed real estate brokers registered in Daegu Dong-gu district."""
        return self._call(
            self._DAEGU_DONGGU_BROKERS,
            config.PUBLIC_DATA_API_KEY or "",
            _p(
                numOfRows=num_rows,
                pageNo=page,
                **{k: v for k, v in kwargs.items() if v is not None},
            ),
        )

    def daegu_donggu_mandatory_managed_apartments(
        self, num_rows: int = 1000, page: int = 1, **kwargs
    ) -> dict:
        """대구광역시 동구 의무관리대상 아파트 현황 — apartments subject to mandatory management regulations in Daegu Dong-gu."""
        return self._call(
            self._DAEGU_DONGGU_APARTMENTS,
            config.PUBLIC_DATA_API_KEY or "",
            _p(
                numOfRows=num_rows,
                pageNo=page,
                **{k: v for k, v in kwargs.items() if v is not None},
            ),
        )

    def daegu_donggu_maintenance_project_status(
        self, num_rows: int = 1000, page: int = 1, **kwargs
    ) -> dict:
        """대구광역시 동구 정비사업 현황 — urban redevelopment and maintenance project status in Daegu Dong-gu."""
        return self._call(
            self._DAEGU_DONGGU_MAINTENANCE,
            config.PUBLIC_DATA_API_KEY or "",
            _p(
                numOfRows=num_rows,
                pageNo=page,
                **{k: v for k, v in kwargs.items() if v is not None},
            ),
        )

    def yeongdeok_individual_house_prices(
        self, num_rows: int = 1000, page: int = 1, **kwargs
    ) -> dict:
        """경상북도 영덕군 개별주택가격 — officially assessed individual house prices in Yeongdeok, North Gyeongsang Province."""
        return self._call(
            self._YEONGDEOK_HOUSE_PRICE,
            config.PUBLIC_DATA_API_KEY or "",
            _p(
                numOfRows=num_rows,
                pageNo=page,
                **{k: v for k, v in kwargs.items() if v is not None},
            ),
        )

    def sangju_building_standard_values(
        self, num_rows: int = 1000, page: int = 1, **kwargs
    ) -> dict:
        """경상북도 상주시 일반 건축물 시가 표준액 — standard assessed values for general buildings in Sangju, North Gyeongsang Province."""
        return self._call(
            self._SANGJU_BUILDING_VALUE,
            config.PUBLIC_DATA_API_KEY or "",
            _p(
                numOfRows=num_rows,
                pageNo=page,
                **{k: v for k, v in kwargs.items() if v is not None},
            ),
        )

    def yeongju_land_property(self, num_rows: int = 1000, page: int = 1, **kwargs) -> dict:
        """경상북도 영주시 토지재산 — land property records in Yeongju, North Gyeongsang Province."""
        return self._call(
            self._YEONGJU_LAND_PROPERTY,
            config.PUBLIC_DATA_API_KEY or "",
            _p(
                numOfRows=num_rows,
                pageNo=page,
                **{k: v for k, v in kwargs.items() if v is not None},
            ),
        )

    def yeongju_use_district(self, num_rows: int = 1000, page: int = 1, **kwargs) -> dict:
        """경상북도 영주시 용도지구 — land use district designations in Yeongju."""
        return self._call(
            self._YEONGJU_USE_DISTRICT,
            config.PUBLIC_DATA_API_KEY or "",
            _p(
                numOfRows=num_rows,
                pageNo=page,
                **{k: v for k, v in kwargs.items() if v is not None},
            ),
        )

    def yeongju_development_permits(self, num_rows: int = 1000, page: int = 1, **kwargs) -> dict:
        """경상북도 영주시 개발행위 허가내역 — development activity permit history in Yeongju."""
        return self._call(
            self._YEONGJU_DEV_PERMITS,
            config.PUBLIC_DATA_API_KEY or "",
            _p(
                numOfRows=num_rows,
                pageNo=page,
                **{k: v for k, v in kwargs.items() if v is not None},
            ),
        )

    def yeongju_forest_land_conversion_permits(
        self, num_rows: int = 1000, page: int = 1, **kwargs
    ) -> dict:
        """경상북도 영주시 산지전용허가 현황 — forest land conversion permit status in Yeongju."""
        return self._call(
            self._YEONGJU_FOREST_CONVERSION,
            config.PUBLIC_DATA_API_KEY or "",
            _p(
                numOfRows=num_rows,
                pageNo=page,
                **{k: v for k, v in kwargs.items() if v is not None},
            ),
        )

    def yeongju_farmland_conversion_permits(
        self, num_rows: int = 1000, page: int = 1, **kwargs
    ) -> dict:
        """경상북도 영주시 농지전용허가 현황 — farmland conversion permit status in Yeongju."""
        return self._call(
            self._YEONGJU_FARMLAND_CONVERSION,
            config.PUBLIC_DATA_API_KEY or "",
            _p(
                numOfRows=num_rows,
                pageNo=page,
                **{k: v for k, v in kwargs.items() if v is not None},
            ),
        )

    def yeongju_local_tax_arrears(self, num_rows: int = 1000, page: int = 1, **kwargs) -> dict:
        """경상북도 영주시 연도별 지방세 체납현황 — annual local tax arrears records in Yeongju."""
        return self._call(
            self._YEONGJU_LOCAL_TAX_ARREARS,
            config.PUBLIC_DATA_API_KEY or "",
            _p(
                numOfRows=num_rows,
                pageNo=page,
                **{k: v for k, v in kwargs.items() if v is not None},
            ),
        )

    # -------------------------------------------------------------------------
    # SECTION: Other National APIs
    # -------------------------------------------------------------------------

    _PUBLIC_STATS_LIST = "1613000/pubStorgeOpenApiService"
    _ISSUANCE_TAX_BY_YEAR = "1741000/IssuanceTaxByYear"
    _BANKRUPTCY_REAL_ESTATE = "B190017/service/GetBankruptcyEstatesGoodsService202307"

    def public_data_statistics_list(self, num_rows: int = 100, page: int = 1, **kwargs) -> dict:
        """공동저장소 통계리스트 — list of available statistical datasets in the public data common storage."""
        return self._call(
            self._PUBLIC_STATS_LIST,
            config.PUBLIC_DATA_API_KEY or "",
            _p(
                numOfRows=num_rows,
                pageNo=page,
                **{k: v for k, v in kwargs.items() if v is not None},
            ),
        )

    def issuance_tax_grant_by_year(self, num_rows: int = 1000, page: int = 1, **kwargs) -> dict:
        """행정안전부 연도별 교부세 — annual local government grants (교부세) statistics from Ministry of the Interior."""
        return self._call(
            self._ISSUANCE_TAX_BY_YEAR,
            config.PUBLIC_DATA_API_KEY or "",
            _p(
                numOfRows=num_rows,
                pageNo=page,
                **{k: v for k, v in kwargs.items() if v is not None},
            ),
        )

    def bankruptcy_institution_real_estate_listings(
        self, num_rows: int = 100, page: int = 1, **kwargs
    ) -> dict:
        """예금보험공사 파산금융회사 매물현황(부동산) — real estate properties for sale from bankrupt financial institutions managed by Korea Deposit Insurance Corporation."""
        return self._call(
            self._BANKRUPTCY_REAL_ESTATE,
            config.PUBLIC_DATA_API_KEY or "",
            _p(
                numOfRows=num_rows,
                pageNo=page,
                **{k: v for k, v in kwargs.items() if v is not None},
            ),
        )
