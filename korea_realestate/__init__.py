"""Korea Real Estate API — Python client for Korean public real estate data."""

from .clients import (
    KoreaRealEstateClient,
    EventsClient,
    LandClient,
    BuildingClient,
    MarketClient,
    AddressClient,
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
    "KoreaRealEstateClient",
    "EventsClient",
    "LandClient",
    "BuildingClient",
    "MarketClient",
    "AddressClient",
    "KoreaRealEstateError",
    "APIKeyError",
    "RateLimitError",
    "RegionNotFoundError",
    "APIResponseError",
]
