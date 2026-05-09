"""HTTP client for https://www.reb.or.kr/r-one/openapi — one method per endpoint."""

import xmltodict

from .. import config
from ..exceptions import (
    APIKeyError,
    APIResponseError,
    InvalidParameterError,
    MissingParameterError,
    NoDataFoundError,
    RateLimitError,
    ServerSideError,
)
from .base_http_client import BaseHttpClient

_BASE = "https://www.reb.or.kr/r-one/openapi/"
_STATS_TABLE_LIST = "SttsApiTbl.do"
_STATS_ITEM_LIST = "SttsApiTblItm.do"
_STATS_DATA = "SttsApiTblData.do"

_TABLE_IDS = {
    "land": "TBL_LND_CHGRT",
    "housing": "TBL_HSG_PRICE",
}


def _p(**kwargs) -> dict:
    return {k: v for k, v in kwargs.items() if v is not None}


def _parse_reb_xml(raw: str, root_element: str) -> dict:
    """Parse REB XML into a normalised dict with code/message/total_count/rows."""
    parsed = xmltodict.parse(raw, force_list=("row",))
    root = parsed.get(root_element, {})
    head = root.get("head", {})
    result = head.get("RESULT", {})
    return {
        "code": result.get("CODE", "INFO-000"),
        "message": result.get("MESSAGE", ""),
        "total_count": int(head.get("list_total_count", 0) or 0),
        "rows": root.get("row") or [],
    }


def _check_reb_result(data: dict) -> None:
    """Raise typed exceptions for REB error codes."""
    code = data.get("code", "INFO-000")
    msg = data.get("message", "")
    if code == "INFO-000":
        return
    if code == "INFO-200":
        raise NoDataFoundError(f"No data found ({code}): {msg}")
    if code in ("INFO-300", "ERROR-290"):
        raise APIKeyError(f"API key error ({code}): {msg}")
    if code == "ERROR-300":
        raise MissingParameterError(f"Required parameter missing ({code}): {msg}")
    if code in ("ERROR-333", "ERROR-336"):
        raise InvalidParameterError(f"Invalid parameter ({code}): {msg}")
    if code == "ERROR-337":
        raise RateLimitError(f"Daily traffic limit exceeded ({code}): {msg}")
    if code == "ERROR-310":
        raise APIResponseError(f"Service not found ({code}): {msg}")
    if code in ("ERROR-500", "ERROR-600", "ERROR-601"):
        raise ServerSideError(f"Server error ({code}): {msg}")
    raise APIResponseError(f"REB API error ({code}): {msg}")


class RebClient(BaseHttpClient):
    """
    All calls to reb.or.kr stats API.
    Auth: KEY query param, injected here.
    Returns normalised dict: {code, message, total_count, rows}.
    """

    def _reb_get(self, path: str, params: dict, root_element: str) -> dict:
        raw = self._raw_get(
            _BASE + path,
            {"KEY": config.REB_API_KEY, "Type": "xml", **params},
        )
        data = _parse_reb_xml(raw, root_element)
        _check_reb_result(data)
        return data

    def statistics_table_list(
        self,
        statbl_id: str | None = None,
        page: int = 1,
        page_size: int = 100,
    ) -> dict:
        """서비스 통계목록 — list of available statistics tables from REB OpenAPI."""
        return self._reb_get(
            _STATS_TABLE_LIST,
            _p(STATBL_ID=statbl_id, pIndex=page, pSize=page_size),
            "SttsApiTbl",
        )

    def statistics_item_list(
        self,
        statbl_id: str,
        itm_tag: str | None = None,
        page: int = 1,
        page_size: int = 100,
    ) -> dict:
        """통계 세부항목 목록 — detailed statistical sub-items for a table (STATBL_ID required)."""
        return self._reb_get(
            _STATS_ITEM_LIST,
            _p(STATBL_ID=statbl_id, ITM_TAG=itm_tag, pIndex=page, pSize=page_size),
            "SttsApiTblItm",
        )

    def statistics_data(
        self,
        statbl_id: str,
        cycle_code: str,
        write_time_id: str | None = None,
        grp_id: str | None = None,
        cls_id: str | None = None,
        itm_id: str | None = None,
        start_write_time: str | None = None,
        end_write_time: str | None = None,
        page: int = 1,
        page_size: int = 100,
    ) -> dict:
        """통계 조회 조건 설정 — query statistical data for a table by cycle, period, and classification."""
        return self._reb_get(
            _STATS_DATA,
            _p(
                STATBL_ID=statbl_id,
                DTACYCLE_CD=cycle_code,
                WRTTIME_IDTFR_ID=write_time_id,
                GRP_ID=grp_id,
                CLS_ID=cls_id,
                ITM_ID=itm_id,
                START_WRTTIME=start_write_time,
                END_WRTTIME=end_write_time,
                pIndex=page,
                pSize=page_size,
            ),
            "SttsApiTblData",
        )

    def real_estate_price_index(
        self,
        region_code: str,
        index_type: str = "land",
        start_year_month: str | None = None,
        end_year_month: str | None = None,
        page_size: int = 500,
        page: int = 1,
    ) -> dict:
        """지가변동률 / 주택가격동향 — land or housing price index for a region and period."""
        if index_type not in _TABLE_IDS:
            raise ValueError(f"index_type must be 'land' or 'housing', got {index_type!r}.")
        return self._reb_get(
            _STATS_DATA,
            _p(
                STATBL_ID=_TABLE_IDS[index_type],
                DTACYCLE_CD="MM",
                CLS_ID=region_code,
                START_WRTTIME=start_year_month,
                END_WRTTIME=end_year_month,
                pIndex=page,
                pSize=page_size,
            ),
            "SttsApiTblData",
        )
