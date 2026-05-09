"""Shared HTTP base: retry logic, XML/JSON parsing, typed error raising."""

import asyncio
import logging
import time
from typing import Any

import httpx
import xmltodict

from ..config import MAX_RETRIES, REQUEST_TIMEOUT_SECONDS
from ..exceptions import APIKeyError, APIResponseError, RateLimitError

logger = logging.getLogger(__name__)

_RETRYABLE_STATUS = {429, 500, 502, 503, 504}


def _parse_response(raw: str) -> dict:
    raw = raw.strip()
    if raw.startswith("<"):
        return xmltodict.parse(raw)
    import json
    return json.loads(raw)


def _check_result_code(data: dict) -> None:
    response = data.get("response", data)
    header = response.get("header", {})
    result_code = str(header.get("resultCode", "00"))
    result_msg = header.get("resultMsg", "")

    if result_code == "30":
        raise APIKeyError(f"Invalid or expired API key: {result_msg}")
    if result_code == "22":
        raise RateLimitError(f"Daily call limit exceeded: {result_msg}")
    if result_code not in ("00", "0000"):
        raise APIResponseError(f"API error {result_code}: {result_msg}")


class BaseHttpClient:
    """Shared retry/parse/error logic. Subclasses inject auth and base URL."""

    def _get(self, url: str, params: dict[str, Any]) -> dict:
        attempt = 0
        last_exc: Exception | None = None

        while attempt <= MAX_RETRIES:
            try:
                logger.debug("GET %s params=%s attempt=%d", url, params, attempt + 1)
                with httpx.Client(timeout=REQUEST_TIMEOUT_SECONDS) as client:
                    resp = client.get(url, params=params)

                if resp.status_code in _RETRYABLE_STATUS:
                    wait = 2 ** attempt
                    logger.warning("HTTP %d — retrying in %ds", resp.status_code, wait)
                    time.sleep(wait)
                    attempt += 1
                    continue

                resp.raise_for_status()
                data = _parse_response(resp.text)
                _check_result_code(data)
                return data

            except (APIKeyError, RateLimitError, APIResponseError):
                raise
            except httpx.HTTPStatusError as exc:
                last_exc = exc
                if exc.response.status_code not in _RETRYABLE_STATUS:
                    raise APIResponseError(str(exc)) from exc
            except httpx.RequestError as exc:
                last_exc = exc
                wait = 2 ** attempt
                logger.warning("Request error: %s — retrying in %ds", exc, wait)
                time.sleep(wait)

            attempt += 1

        raise APIResponseError(f"Request failed after {MAX_RETRIES} retries") from last_exc

    async def _aget(self, url: str, params: dict[str, Any]) -> dict:
        attempt = 0
        last_exc: Exception | None = None

        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
            while attempt <= MAX_RETRIES:
                try:
                    logger.debug("GET %s params=%s attempt=%d", url, params, attempt + 1)
                    resp = await client.get(url, params=params)

                    if resp.status_code in _RETRYABLE_STATUS:
                        wait = 2 ** attempt
                        logger.warning("HTTP %d — retrying in %ds", resp.status_code, wait)
                        await asyncio.sleep(wait)
                        attempt += 1
                        continue

                    resp.raise_for_status()
                    data = _parse_response(resp.text)
                    _check_result_code(data)
                    return data

                except (APIKeyError, RateLimitError, APIResponseError):
                    raise
                except httpx.HTTPStatusError as exc:
                    last_exc = exc
                    if exc.response.status_code not in _RETRYABLE_STATUS:
                        raise APIResponseError(str(exc)) from exc
                except httpx.RequestError as exc:
                    last_exc = exc
                    wait = 2 ** attempt
                    logger.warning("Request error: %s — retrying in %ds", exc, wait)
                    await asyncio.sleep(wait)

                attempt += 1

        raise APIResponseError(f"Request failed after {MAX_RETRIES} retries") from last_exc
