from __future__ import annotations

import json
import math
import platform
import random
import time
from collections.abc import Mapping
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any

import httpx

from ._request_options import RequestOptions
from ._version import __version__
from .errors import APIError


def _normalized_os() -> str:
    os_name = platform.system().lower()
    if os_name == "darwin":
        return "MacOS"
    if os_name == "windows":
        return "Windows"
    if os_name == "linux":
        return "Linux"
    return f"Other:{platform.system()}"


def _normalized_arch() -> str:
    arch = platform.machine().lower()
    if arch in {"x86_64", "amd64"}:
        return "x64"
    if arch in {"i386", "i686", "x86"}:
        return "x32"
    if arch in {"arm64", "aarch64"}:
        return "arm64"
    if arch.startswith("arm"):
        return "arm"
    return f"other:{platform.machine()}"


def _is_json_content_type(content_type: str) -> bool:
    media_type = content_type.split(";", 1)[0].strip().lower()
    return media_type == "application/json" or media_type.endswith("+json")


def _parse_retry_after(resp: httpx.Response | None) -> float | None:
    if resp is None:
        return None

    retry_after_ms = resp.headers.get("Retry-After-Ms")
    if retry_after_ms:
        try:
            return max(0.0, float(retry_after_ms) / 1000.0)
        except ValueError:
            pass

    retry_after = resp.headers.get("Retry-After")
    if not retry_after:
        return None

    try:
        return max(0.0, float(retry_after))
    except ValueError:
        pass

    try:
        parsed = parsedate_to_datetime(retry_after)
    except (TypeError, ValueError):
        return None

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)

    return max(0.0, (parsed - datetime.now(timezone.utc)).total_seconds())


def _retry_delay(resp: httpx.Response | None, retry_count: int) -> float:
    hinted = _parse_retry_after(resp)
    if hinted is not None:
        return hinted

    delay = min(0.5 * math.pow(2, retry_count), 8.0)
    jitter = random.uniform(0, delay / 4)
    return delay - jitter


def _should_retry(resp: httpx.Response | None, err: Exception | None) -> bool:
    if err is not None:
        return True

    if resp is None:
        return True

    explicit = resp.headers.get("x-should-retry")
    if explicit == "true":
        return True
    if explicit == "false":
        return False

    return resp.status_code in {408, 409, 429} or resp.status_code >= 500


class HTTPTransport:
    """Shared HTTP runtime for Linq SDK services."""

    def __init__(
        self,
        *,
        api_key: str | None,
        base_url: str,
        timeout: float | None,
        max_retries: int,
        http_client: httpx.Client | None = None,
        default_headers: Mapping[str, str] | None = None,
    ) -> None:
        if max_retries < 0:
            raise ValueError("max_retries cannot be negative")

        self._api_key = api_key
        self._timeout = timeout
        self._max_retries = max_retries

        self._owns_client = http_client is None
        normalized_base_url = httpx.URL(base_url)
        if normalized_base_url.path and not normalized_base_url.path.endswith("/"):
            normalized_base_url = normalized_base_url.copy_with(path=f"{normalized_base_url.path}/")
        self._base_url = normalized_base_url

        self._client = http_client or httpx.Client(base_url=str(self._base_url), timeout=timeout)

        self._base_headers = {
            "User-Agent": f"LinqAPIV3/Python {__version__}",
            "Accept": "application/json",
            "X-Stainless-Lang": "python",
            "X-Stainless-Package-Version": __version__,
            "X-Stainless-OS": _normalized_os(),
            "X-Stainless-Arch": _normalized_arch(),
            "X-Stainless-Runtime": "python",
            "X-Stainless-Runtime-Version": platform.python_version(),
            "X-Stainless-Retry-Count": "0",
        }

        if default_headers:
            self._base_headers.update(default_headers)

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def request(
        self,
        method: str,
        path: str,
        *,
        body: Any | None = None,
        query: Mapping[str, Any] | None = None,
        options: RequestOptions | None = None,
        parse_json: bool = True,
    ) -> Any:
        headers = dict(self._base_headers)
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"

        if options and options.headers:
            headers.update(options.headers)

        timeout = self._timeout
        if options and options.timeout is not None:
            timeout = options.timeout

        if timeout is None:
            headers.pop("X-Stainless-Timeout", None)
        elif "X-Stainless-Timeout" not in headers:
            headers["X-Stainless-Timeout"] = str(int(timeout))

        max_retries = self._max_retries
        if options and options.max_retries is not None:
            max_retries = options.max_retries
        if max_retries < 0:
            raise ValueError("max_retries cannot be negative")

        final_query: dict[str, Any] = {}
        if query:
            final_query.update(query)
        if options and options.query:
            final_query.update(options.query)

        request_content: bytes | None = None
        if options and options.raw_body is not None:
            raw = options.raw_body
            if isinstance(raw, str):
                request_content = raw.encode("utf-8")
            else:
                request_content = raw
            if options.content_type:
                headers["Content-Type"] = options.content_type
        elif body is not None:
            request_content = json.dumps(body).encode("utf-8")
            headers.setdefault("Content-Type", "application/json")

        send_retry_count = headers.get("X-Stainless-Retry-Count") == "0"

        response: httpx.Response | None = None
        transport_error: Exception | None = None

        for attempt in range(max_retries + 1):
            attempt_headers = dict(headers)
            if send_retry_count:
                attempt_headers["X-Stainless-Retry-Count"] = str(attempt)

            try:
                raw_url = httpx.URL(path)
                url = raw_url if raw_url.is_absolute_url else self._base_url.join(path.lstrip("/"))

                response = self._client.request(
                    method=method,
                    url=url,
                    params=final_query or None,
                    headers=attempt_headers,
                    content=request_content,
                    timeout=timeout,
                )
                transport_error = None
            except httpx.TransportError as exc:
                transport_error = exc
                response = None

            if not _should_retry(response, transport_error) or attempt >= max_retries:
                break

            time.sleep(_retry_delay(response, attempt))

        if transport_error is not None:
            raise transport_error

        if response is None:
            raise RuntimeError("request failed before receiving a response")

        if response.status_code >= 400:
            raise APIError(
                status_code=response.status_code,
                method=method.upper(),
                url=str(response.request.url),
                body=response.text,
                response=response,
            )

        if not parse_json:
            return None

        if response.status_code == 204 or not response.content:
            return None

        content_type = response.headers.get("content-type", "")
        if not _is_json_content_type(content_type):
            return response.text

        return response.json()
