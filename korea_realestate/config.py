import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")


def _get(key: str, default: str | None = None) -> str | None:
    return os.environ.get(key, default)


def _require(key: str) -> str:
    val = os.environ.get(key)
    if not val or val == "your_service_key_here":
        raise EnvironmentError(
            f"Environment variable '{key}' is not set. "
            f"Copy .env.example to .env and fill in your API keys from https://www.data.go.kr"
        )
    return val


SALES_HISTORY_API_KEY: str | None = _get("SALES_HISTORY_API_KEY")
PRICE_TRENDS_API_KEY: str | None = _get("PRICE_TRENDS_API_KEY")
APPRAISED_VALUE_API_KEY: str | None = _get("APPRAISED_VALUE_API_KEY")
ZONING_API_KEY: str | None = _get("ZONING_API_KEY")

DEFAULT_REGION_CODE: str = _get("DEFAULT_REGION_CODE", "42820")
REQUEST_TIMEOUT_SECONDS: int = int(_get("REQUEST_TIMEOUT_SECONDS", "30"))
MAX_RETRIES: int = int(_get("MAX_RETRIES", "3"))


def require_sales_history_key() -> str:
    return _require("SALES_HISTORY_API_KEY")


def require_price_trends_key() -> str:
    return _require("PRICE_TRENDS_API_KEY")


def require_appraised_value_key() -> str:
    return _require("APPRAISED_VALUE_API_KEY")


def require_zoning_key() -> str:
    return _require("ZONING_API_KEY")
