__all__ = [
    "KoreaRealEstateError",
    "APIKeyError",
    "RateLimitError",
    "RegionNotFoundError",
    "APIResponseError",
    "InvalidParameterError",
    "MissingParameterError",
    "NoDataFoundError",
    "ServerSideError",
    "NetworkError",
]


class KoreaRealEstateError(Exception):
    """Base exception for all Korea Real Estate API errors."""


class APIKeyError(KoreaRealEstateError):
    """Raised when an API key is missing, invalid, or expired."""


class RateLimitError(KoreaRealEstateError):
    """Raised when the API rate limit (typically 1,000/day) is exceeded."""


class RegionNotFoundError(KoreaRealEstateError):
    """Raised when the provided region code returns no data."""


class APIResponseError(KoreaRealEstateError):
    """Raised for unexpected API response structures or HTTP errors."""


class InvalidParameterError(APIResponseError):
    """API returned error code 10/51: invalid request parameter."""


class MissingParameterError(APIResponseError):
    """API returned error code 11/52: required parameter missing."""


class NoDataFoundError(KoreaRealEstateError):
    """API returned error code 03/50: no data found for query."""


class ServerSideError(KoreaRealEstateError):
    """API returned error code 01/02/500: server-side error."""


class NetworkError(KoreaRealEstateError):
    """Connection or timeout error reaching the API."""
