from __future__ import annotations

import httpx


class APIError(Exception):
    """Raised when the Linq API returns a 4xx/5xx response."""

    def __init__(
        self,
        *,
        status_code: int,
        method: str,
        url: str,
        body: str,
        response: httpx.Response,
    ) -> None:
        self.status_code = status_code
        self.method = method
        self.url = url
        self.body = body
        self.response = response
        super().__init__(f"{method} {url!r}: {status_code} {body}")
