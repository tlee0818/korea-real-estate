"""HTTP client for https://www.reb.or.kr/r-one/openapi — one method per endpoint."""

from .. import config
from .base_http_client import BaseHttpClient

_BASE = "https://www.reb.or.kr/r-one/openapi/"
_PRICE_INDEX = "SttsApiTblData.do"

_TABLE_IDS = {
    "land": "TBL_LND_CHGRT",
    "housing": "TBL_HSG_PRICE",
}


def _p(**kwargs) -> dict:
    return {k: v for k, v in kwargs.items() if v is not None}


class RebClient(BaseHttpClient):
    """
    All calls to reb.or.kr stats API.
    Auth: KEY query param, injected here.
    """

    def _call(self, path: str, params: dict) -> dict:
        return self._get(_BASE + path, {"KEY": config.REB_API_KEY, **params})

    def real_estate_price_index(
        self,
        region_code: str,
        index_type: str = "land",
        start_year_month: str | None = None,
        end_year_month: str | None = None,
        num_rows: int = 500,
    ) -> dict:
        """
        지가변동률 / 주택가격동향 — land or housing price index for a region and period.

        Args:
            region_code: 5-digit 시군구 code.
            index_type: "land" or "housing".
            start_year_month: YYYYMM (optional).
            end_year_month: YYYYMM (optional).
            num_rows: Max rows to return.
        """
        if index_type not in _TABLE_IDS:
            raise ValueError(f"index_type must be 'land' or 'housing', got {index_type!r}.")
        return self._call(
            _PRICE_INDEX,
            _p(
                tblId=_TABLE_IDS[index_type],
                regionCode=region_code,
                startPeriod=start_year_month,
                endPeriod=end_year_month,
                format="xml",
                numOfRows=num_rows,
                pageNo=1,
            ),
        )
