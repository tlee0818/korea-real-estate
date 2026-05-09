"""Korea Real Estate API — Python client for Korean public real estate data."""

from .client import KoreaRealEstateClient
from .http.public_data import PublicDataClient
from .http.reb import RebClient
from .http.juso import JusoClient
from .exceptions import (
    APIKeyError,
    APIResponseError,
    KoreaRealEstateError,
    RateLimitError,
    RegionNotFoundError,
)

__version__ = "0.2.1"

__all__ = [
    "KoreaRealEstateClient",
    "PublicDataClient",
    "RebClient",
    "JusoClient",
    "KoreaRealEstateError",
    "APIKeyError",
    "RateLimitError",
    "RegionNotFoundError",
    "APIResponseError",
]
