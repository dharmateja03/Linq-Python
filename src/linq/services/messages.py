from __future__ import annotations

from collections.abc import Mapping
from typing import Any
from urllib.parse import quote

from .._http import HTTPTransport
from .._pagination import AutoPager, CursorPage
from .._request_options import RequestOptions, merge_request_options


def _require(value: str, name: str) -> str:
    if not value:
        raise ValueError(f"missing required {name} parameter")
    return value


class MessagesService:
    def __init__(self, transport: HTTPTransport) -> None:
        self._transport = transport

    def get(self, message_id: str, *, options: RequestOptions | None = None) -> dict[str, Any]:
        message_id = quote(_require(message_id, "message_id"), safe="")
        return self._transport.request("GET", f"v3/messages/{message_id}", options=options)

    def update(
        self,
        message_id: str,
        body: Mapping[str, Any],
        *,
        options: RequestOptions | None = None,
    ) -> dict[str, Any]:
        message_id = quote(_require(message_id, "message_id"), safe="")
        return self._transport.request(
            "PATCH",
            f"v3/messages/{message_id}",
            body=body,
            options=options,
        )

    def delete(self, message_id: str, *, options: RequestOptions | None = None) -> None:
        message_id = quote(_require(message_id, "message_id"), safe="")
        options = merge_request_options(options, headers={"Accept": "*/*"})
        self._transport.request(
            "DELETE",
            f"v3/messages/{message_id}",
            options=options,
            parse_json=False,
        )

    def add_reaction(
        self,
        message_id: str,
        body: Mapping[str, Any],
        *,
        options: RequestOptions | None = None,
    ) -> dict[str, Any]:
        message_id = quote(_require(message_id, "message_id"), safe="")
        return self._transport.request(
            "POST",
            f"v3/messages/{message_id}/reactions",
            body=body,
            options=options,
        )

    def list_messages_thread(
        self,
        message_id: str,
        query: Mapping[str, Any] | None = None,
        *,
        options: RequestOptions | None = None,
    ) -> CursorPage[dict[str, Any]]:
        message_id = quote(_require(message_id, "message_id"), safe="")
        base_query = dict(query or {})

        def fetch(cursor: str) -> dict[str, Any]:
            next_query = dict(base_query)
            next_query["cursor"] = cursor
            return self._transport.request(
                "GET",
                f"v3/messages/{message_id}/thread",
                query=next_query,
                options=options,
            )

        payload = self._transport.request(
            "GET",
            f"v3/messages/{message_id}/thread",
            query=base_query,
            options=options,
        )
        return CursorPage(_item_key="messages", _payload=payload, _fetch_next=fetch)

    def list_messages_thread_auto_paging(
        self,
        message_id: str,
        query: Mapping[str, Any] | None = None,
        *,
        options: RequestOptions | None = None,
    ) -> AutoPager[dict[str, Any]]:
        return AutoPager(self.list_messages_thread(message_id, query, options=options))
