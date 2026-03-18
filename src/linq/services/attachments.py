from __future__ import annotations

from collections.abc import Mapping
from typing import Any
from urllib.parse import quote

from .._http import HTTPTransport
from .._request_options import RequestOptions


def _require(value: str, name: str) -> str:
    if not value:
        raise ValueError(f"missing required {name} parameter")
    return value


class AttachmentsService:
    def __init__(self, transport: HTTPTransport) -> None:
        self._transport = transport

    def create(
        self,
        body: Mapping[str, Any],
        *,
        options: RequestOptions | None = None,
    ) -> dict[str, Any]:
        return self._transport.request("POST", "v3/attachments", body=body, options=options)

    def get(
        self,
        attachment_id: str,
        *,
        options: RequestOptions | None = None,
    ) -> dict[str, Any]:
        attachment_id = quote(_require(attachment_id, "attachment_id"), safe="")
        return self._transport.request("GET", f"v3/attachments/{attachment_id}", options=options)

    # Go-style alias
    new = create
