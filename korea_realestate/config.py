import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")


def _get(key: str, default: str | None = None) -> str | None:
    return os.environ.get(key, default)


def _require(key: str) -> str:
    val = os.environ.get(key)
    if not val or val == "your_key_here":
        raise EnvironmentError(
            f"Environment variable '{key}' is not set. "
            f"Copy .env.example to .env and fill in your API keys from https://www.data.go.kr"
        )
    return val


# EventsClient keys
SALES_HISTORY_API_KEY: str | None = _get("SALES_HISTORY_API_KEY")
COMMERCIAL_SALES_API_KEY: str | None = _get("COMMERCIAL_SALES_API_KEY")
BUILDING_PERMITS_API_KEY: str | None = _get("BUILDING_PERMITS_API_KEY")

# LandClient keys
ZONING_API_KEY: str | None = _get("ZONING_API_KEY")
APPRAISED_VALUE_API_KEY: str | None = _get("APPRAISED_VALUE_API_KEY")
STANDARD_LAND_PRICE_API_KEY: str | None = _get("STANDARD_LAND_PRICE_API_KEY")

# BuildingClient keys
BUILDING_REGISTRY_API_KEY: str | None = _get("BUILDING_REGISTRY_API_KEY")
BUILDING_MAP_API_KEY: str | None = _get("BUILDING_MAP_API_KEY")

# MarketClient key
PRICE_TRENDS_API_KEY: str | None = _get("PRICE_TRENDS_API_KEY")

# AddressClient key
ADDRESS_RESOLVER_API_KEY: str | None = _get("ADDRESS_RESOLVER_API_KEY")

# Shared defaults
DEFAULT_REGION_CODE: str = _get("DEFAULT_REGION_CODE", "42820")
REQUEST_TIMEOUT_SECONDS: int = int(_get("REQUEST_TIMEOUT_SECONDS", "30"))
MAX_RETRIES: int = int(_get("MAX_RETRIES", "3"))
