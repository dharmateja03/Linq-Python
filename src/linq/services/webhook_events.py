from __future__ import annotations

from typing import Any

from .._http import HTTPTransport
from .._request_options import RequestOptions


class WebhookEventsService:
    def __init__(self, transport: HTTPTransport) -> None:
        self._transport = transport

    def list(self, *, options: RequestOptions | None = None) -> dict[str, Any]:
        return self._transport.request("GET", "v3/webhook-events", options=options)
