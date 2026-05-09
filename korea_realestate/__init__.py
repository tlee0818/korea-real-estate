"""Korea Real Estate API — Python client for Korean public real estate data."""

from .client import KoreaRealEstateClient
from .exceptions import (
    APIKeyError,
    APIResponseError,
    InvalidParameterError,
    KoreaRealEstateError,
    MissingParameterError,
    NetworkError,
    NoDataFoundError,
    RateLimitError,
    RegionNotFoundError,
    ServerSideError,
)
from .http.juso import JusoClient
from .http.public_data import PublicDataClient
from .http.reb import RebClient

__version__ = "4.15.1"

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
    "InvalidParameterError",
    "MissingParameterError",
    "NoDataFoundError",
    "ServerSideError",
    "NetworkError",
]
