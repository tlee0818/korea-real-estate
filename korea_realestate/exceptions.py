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
