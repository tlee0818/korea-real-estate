"""Korea Real Estate API — Python client for Korean public real estate data."""

from .clients import (
    AppraisedValueClient,
    PriceTrendsClient,
    SalesHistoryClient,
    ZoningClient,
)
from .exceptions import (
    APIKeyError,
    APIResponseError,
    KoreaRealEstateError,
    RateLimitError,
    RegionNotFoundError,
)

__version__ = "0.1.0"

__all__ = [
    "SalesHistoryClient",
    "PriceTrendsClient",
    "AppraisedValueClient",
    "ZoningClient",
    "KoreaRealEstateError",
    "APIKeyError",
    "RateLimitError",
    "RegionNotFoundError",
    "APIResponseError",
]
