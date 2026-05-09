"""Shared HTTP base: retry logic, XML/JSON parsing, typed error raising."""

import asyncio
import logging
import time
from typing import Any

import httpx
import xmltodict

from ..config import MAX_RETRIES, REQUEST_TIMEOUT_SECONDS
from ..exceptions import (
    APIKeyError,
    APIResponseError,
    InvalidParameterError,
    KoreaRealEstateError,
    MissingParameterError,
    NetworkError,
    NoDataFoundError,
    RateLimitError,
    ServerSideError,
)

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

    if result_code in ("00", "0000", "200"):
        return
    if result_code == "30":
        raise APIKeyError(f"Invalid or expired API key (code 30): {result_msg}")
    if result_code == "22":
        raise RateLimitError(f"Daily call limit exceeded (code 22): {result_msg}")
    if result_code in ("10", "51"):
        raise InvalidParameterError(f"Invalid request parameter (code {result_code}): {result_msg}")
    if result_code in ("11", "52"):
        raise MissingParameterError(
            f"Required parameter missing (code {result_code}): {result_msg}"
        )
    if result_code in ("03", "50"):
        raise NoDataFoundError(f"No data found (code {result_code}): {result_msg}")
    if result_code == "01":
        raise ServerSideError(f"Application error on server (code 01): {result_msg}")
    if result_code == "02":
        raise ServerSideError(f"Database error on server (code 02): {result_msg}")
    if result_code == "500":
        raise ServerSideError(f"Server internal error (code 500): {result_msg}")
    if result_code == "21":
        raise APIKeyError(f"Service key temporarily unavailable (code 21): {result_msg}")
    if result_code == "33":
        raise APIKeyError(f"Unsigned/unauthorized call (code 33): {result_msg}")
    if result_code == "05":
        raise NetworkError(f"API service connection failed (code 05): {result_msg}")
    raise APIResponseError(f"API error (code {result_code}): {result_msg}")


class BaseHttpClient:
    """Shared retry/parse/error logic. Subclasses inject auth and base URL."""

    def _raw_get(self, url: str, params: dict[str, Any]) -> str:
        """Execute GET with retry logic. Returns raw response text on success."""
        attempt = 0
        last_exc: Exception | None = None

        while attempt <= MAX_RETRIES:
            try:
                logger.debug("GET %s params=%s attempt=%d", url, params, attempt + 1)
                with httpx.Client(timeout=REQUEST_TIMEOUT_SECONDS) as client:
                    resp = client.get(url, params=params)

                if resp.status_code in _RETRYABLE_STATUS:
                    wait = 2**attempt
                    logger.warning("HTTP %d — retrying in %ds", resp.status_code, wait)
                    time.sleep(wait)
                    attempt += 1
                    continue

                resp.raise_for_status()
                return resp.text

            except (KoreaRealEstateError,):
                raise
            except httpx.ConnectError as exc:
                raise NetworkError(f"Network error: could not connect to {url} — {exc}") from exc
            except httpx.TimeoutException as exc:
                raise NetworkError(
                    f"Network error: request to {url} timed out after {REQUEST_TIMEOUT_SECONDS}s — {exc}"
                ) from exc
            except httpx.RemoteProtocolError as exc:
                raise NetworkError(
                    f"Network error: server at {url} returned an invalid response — {exc}"
                ) from exc
            except httpx.HTTPStatusError as exc:
                last_exc = exc
                if exc.response.status_code not in _RETRYABLE_STATUS:
                    raise APIResponseError(str(exc)) from exc
            except httpx.RequestError as exc:
                last_exc = exc
                wait = 2**attempt
                logger.warning("Request error: %s — retrying in %ds", exc, wait)
                time.sleep(wait)

            attempt += 1

        raise NetworkError(f"Network error: {last_exc}") from last_exc

    def _get(self, url: str, params: dict[str, Any]) -> dict:
        raw = self._raw_get(url, params)
        data = _parse_response(raw)
        _check_result_code(data)
        return data

    async def _aget(self, url: str, params: dict[str, Any]) -> dict:
        attempt = 0
        last_exc: Exception | None = None

        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
            while attempt <= MAX_RETRIES:
                try:
                    logger.debug("GET %s params=%s attempt=%d", url, params, attempt + 1)
                    resp = await client.get(url, params=params)

                    if resp.status_code in _RETRYABLE_STATUS:
                        wait = 2**attempt
                        logger.warning("HTTP %d — retrying in %ds", resp.status_code, wait)
                        await asyncio.sleep(wait)
                        attempt += 1
                        continue

                    resp.raise_for_status()
                    data = _parse_response(resp.text)
                    _check_result_code(data)
                    return data

                except (KoreaRealEstateError,):
                    raise
                except httpx.ConnectError as exc:
                    raise NetworkError(
                        f"Network error: could not connect to {url} — {exc}"
                    ) from exc
                except httpx.TimeoutException as exc:
                    raise NetworkError(
                        f"Network error: request to {url} timed out after {REQUEST_TIMEOUT_SECONDS}s — {exc}"
                    ) from exc
                except httpx.RemoteProtocolError as exc:
                    raise NetworkError(
                        f"Network error: server at {url} returned an invalid response — {exc}"
                    ) from exc
                except httpx.HTTPStatusError as exc:
                    last_exc = exc
                    if exc.response.status_code not in _RETRYABLE_STATUS:
                        raise APIResponseError(str(exc)) from exc
                except httpx.RequestError as exc:
                    last_exc = exc
                    wait = 2**attempt
                    logger.warning("Request error: %s — retrying in %ds", exc, wait)
                    await asyncio.sleep(wait)

                attempt += 1

        raise NetworkError(f"Network error: {last_exc}") from last_exc
