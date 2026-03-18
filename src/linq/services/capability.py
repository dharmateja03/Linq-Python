from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .._http import HTTPTransport
from .._request_options import RequestOptions


class CapabilityService:
    def __init__(self, transport: HTTPTransport) -> None:
        self._transport = transport

    def check_imessage(
        self,
        body: Mapping[str, Any],
        *,
        options: RequestOptions | None = None,
    ) -> dict[str, Any]:
        return self._transport.request(
            "POST",
            "v3/capability/check_imessage",
            body=body,
            options=options,
        )

    def check_rcs(
        self,
        body: Mapping[str, Any],
        *,
        options: RequestOptions | None = None,
    ) -> dict[str, Any]:
        return self._transport.request(
            "POST",
            "v3/capability/check_rcs",
            body=body,
            options=options,
        )

    # Go-style aliases
    checkiMessage = check_imessage
    checkRCS = check_rcs
