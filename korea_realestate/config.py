import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")


def _get(key: str, default: str | None = None) -> str | None:
    return os.environ.get(key, default)


# data.go.kr — one key covers all public data portal endpoints
PUBLIC_DATA_API_KEY: str | None = _get("PUBLIC_DATA_API_KEY")

# NSDI (국가공간정보포털) — individual land price; uses 'key' param, separate portal
NSDI_API_KEY: str | None = _get("NSDI_API_KEY")

# REB (한국부동산원) — real estate price index
REB_API_KEY: str | None = _get("REB_API_KEY")

# Juso (도로명주소) — address resolution
JUSO_API_KEY: str | None = _get("JUSO_API_KEY")

# Shared defaults
DEFAULT_REGION_CODE: str = _get("DEFAULT_REGION_CODE", "42820")
REQUEST_TIMEOUT_SECONDS: int = int(_get("REQUEST_TIMEOUT_SECONDS", "30"))
MAX_RETRIES: int = int(_get("MAX_RETRIES", "3"))
