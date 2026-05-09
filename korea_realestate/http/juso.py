"""HTTP client for https://business.juso.go.kr/addrlink — one method per endpoint."""

from .. import config
from .base_http_client import BaseHttpClient

_BASE = "https://business.juso.go.kr/addrlink/"
_RESOLVE = "addrLinkApi.do"


class JusoClient(BaseHttpClient):
    """
    All calls to the Juso address resolution API.
    Auth: confmKey param, encapsulated here. Returns JSON natively.
    """

    def _call(self, path: str, params: dict) -> dict:
        return self._get(_BASE + path, {
            "confmKey": config.ADDRESS_RESOLVER_API_KEY,
            "resultType": "json",
            **{k: v for k, v in params.items() if v is not None},
        })

    def resolve_address(
        self,
        keyword: str,
        count_per_page: int = 10,
        current_page: int = 1,
    ) -> dict:
        """
        도로명주소 API — resolve a Korean address string to structured fields.

        Args:
            keyword: Address string to resolve.
            count_per_page: Results per page (default 10).
            current_page: Page number (default 1).
        """
        return self._call(_RESOLVE, {
            "keyword": keyword,
            "countPerPage": count_per_page,
            "currentPage": current_page,
        })
