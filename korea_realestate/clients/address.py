"""AddressClient — Korean address resolution via the Juso API."""

from __future__ import annotations

from typing import Optional

from ..http.juso import JusoClient

def _parse_juso_item(item: dict) -> dict:
    return {
        "road_address": item.get("roadAddr", "").strip(),
        "parcel_address": item.get("jibunAddr", "").strip(),
        "postal_code": item.get("zipNo", "").strip(),
        "sido": item.get("siNm", "").strip(),
        "sigungu": item.get("sggNm", "").strip(),
        "eupmyeondong": item.get("emdNm", "").strip(),
        "ri": item.get("liNm", "").strip(),
        "sigungu_code": item.get("admCd", "")[:5] if item.get("admCd") else "",
        "bdong_code": item.get("bdKdcd", "").strip(),
        "building_mgmt_no": item.get("bdMgtSn", "").strip(),
        "building_name": item.get("bdNm", "").strip() or None,
        "is_apartment": item.get("mtYn", "0") == "1",
        "latitude": float(item["y"]) if item.get("y") else None,
        "longitude": float(item["x"]) if item.get("x") else None,
    }


class AddressClient:
    """
    Resolves Korean address strings into structured codes.
    Used internally by domain clients to normalize string region inputs.
    API: https://www.data.go.kr/data/15057017/openapi.do (confmKey param, JSON response).
    """

    def __init__(self, http: Optional[JusoClient] = None):
        self._http = http or JusoClient()

    def resolve(self, address: str) -> dict:
        """
        Resolve a single Korean address string.

        Returns:
            Dict with road_address, parcel_address, postal_code, sido, sigungu,
            eupmyeondong, ri, sigungu_code, bdong_code, building_mgmt_no,
            building_name, is_apartment, latitude, longitude.
        """
        data = self._http.resolve_address(keyword=address, count_per_page=1)
        items = data.get("results", {}).get("juso", [])
        if not items:
            raise ValueError(f"Address not found: {address!r}")
        return _parse_juso_item(items[0])

    def resolve_many(self, addresses: list[str]) -> list[dict]:
        """Resolve a list of address strings. Returns list in same order."""
        return [self.resolve(a) for a in addresses]

    def to_region_code(self, address: str) -> str:
        """
        Convenience: address string → 5-digit 시군구 code.
        Used by domain clients to normalize string region inputs.
        """
        result = self.resolve(address)
        code = result.get("sigungu_code", "")
        if not code:
            raise ValueError(f"Could not extract sigungu_code from address: {address!r}")
        return code
