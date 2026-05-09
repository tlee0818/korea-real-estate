"""HTTP client for https://business.juso.go.kr/addrlink — one method per endpoint."""

from .. import config
from .base_http_client import BaseHttpClient

_BASE = "https://business.juso.go.kr/addrlink/"
_LOOKUP = "addrLinkApi.do"


class JusoClient(BaseHttpClient):
    """
    All calls to the Juso address resolution API.
    Auth: confmKey param, injected here. Returns JSON natively.
    """

    def _call(self, path: str, params: dict) -> dict:
        return self._get(_BASE + path, {
            "confmKey": config.JUSO_API_KEY,
            "resultType": "json",
            **{k: v for k, v in params.items() if v is not None},
        })

    def address_lookup(
        self,
        keyword: str,
        count_per_page: int = 10,
        current_page: int = 1,
    ) -> dict:
        """도로명주소 API — resolve a Korean address string to structured road/jibun fields."""
        return self._call(_LOOKUP, {
            "keyword": keyword,
            "countPerPage": count_per_page,
            "currentPage": current_page,
        })
