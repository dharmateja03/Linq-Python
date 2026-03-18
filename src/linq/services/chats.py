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


class ChatParticipantsService:
    def __init__(self, transport: HTTPTransport) -> None:
        self._transport = transport

    def add(
        self,
        chat_id: str,
        body: Mapping[str, Any],
        *,
        options: RequestOptions | None = None,
    ) -> dict[str, Any]:
        chat_id = quote(_require(chat_id, "chat_id"), safe="")
        return self._transport.request(
            "POST",
            f"v3/chats/{chat_id}/participants",
            body=body,
            options=options,
        )

    def remove(
        self,
        chat_id: str,
        body: Mapping[str, Any],
        *,
        options: RequestOptions | None = None,
    ) -> dict[str, Any]:
        chat_id = quote(_require(chat_id, "chat_id"), safe="")
        return self._transport.request(
            "DELETE",
            f"v3/chats/{chat_id}/participants",
            body=body,
            options=options,
        )


class ChatTypingService:
    def __init__(self, transport: HTTPTransport) -> None:
        self._transport = transport

    def start(self, chat_id: str, *, options: RequestOptions | None = None) -> None:
        chat_id = quote(_require(chat_id, "chat_id"), safe="")
        options = merge_request_options(options, headers={"Accept": "*/*"})
        self._transport.request(
            "POST",
            f"v3/chats/{chat_id}/typing",
            options=options,
            parse_json=False,
        )

    def stop(self, chat_id: str, *, options: RequestOptions | None = None) -> None:
        chat_id = quote(_require(chat_id, "chat_id"), safe="")
        options = merge_request_options(options, headers={"Accept": "*/*"})
        self._transport.request(
            "DELETE",
            f"v3/chats/{chat_id}/typing",
            options=options,
            parse_json=False,
        )


class ChatMessagesService:
    def __init__(self, transport: HTTPTransport) -> None:
        self._transport = transport

    def list(
        self,
        chat_id: str,
        query: Mapping[str, Any] | None = None,
        *,
        options: RequestOptions | None = None,
    ) -> CursorPage[dict[str, Any]]:
        chat_id = quote(_require(chat_id, "chat_id"), safe="")
        base_query = dict(query or {})

        def fetch(cursor: str) -> dict[str, Any]:
            next_query = dict(base_query)
            next_query["cursor"] = cursor
            return self._transport.request(
                "GET",
                f"v3/chats/{chat_id}/messages",
                query=next_query,
                options=options,
            )

        payload = self._transport.request(
            "GET",
            f"v3/chats/{chat_id}/messages",
            query=base_query,
            options=options,
        )
        return CursorPage(_item_key="messages", _payload=payload, _fetch_next=fetch)

    def list_auto_paging(
        self,
        chat_id: str,
        query: Mapping[str, Any] | None = None,
        *,
        options: RequestOptions | None = None,
    ) -> AutoPager[dict[str, Any]]:
        return AutoPager(self.list(chat_id, query, options=options))

    def send(
        self,
        chat_id: str,
        body: Mapping[str, Any],
        *,
        options: RequestOptions | None = None,
    ) -> dict[str, Any]:
        chat_id = quote(_require(chat_id, "chat_id"), safe="")
        return self._transport.request(
            "POST",
            f"v3/chats/{chat_id}/messages",
            body=body,
            options=options,
        )


class ChatsService:
    def __init__(self, transport: HTTPTransport) -> None:
        self._transport = transport

        self.participants = ChatParticipantsService(transport)
        self.typing = ChatTypingService(transport)
        self.messages = ChatMessagesService(transport)

        # Go-style aliases
        self.Participants = self.participants
        self.Typing = self.typing
        self.Messages = self.messages

    def create(
        self,
        body: Mapping[str, Any],
        *,
        options: RequestOptions | None = None,
    ) -> dict[str, Any]:
        return self._transport.request("POST", "v3/chats", body=body, options=options)

    def get(self, chat_id: str, *, options: RequestOptions | None = None) -> dict[str, Any]:
        chat_id = quote(_require(chat_id, "chat_id"), safe="")
        return self._transport.request("GET", f"v3/chats/{chat_id}", options=options)

    def update(
        self,
        chat_id: str,
        body: Mapping[str, Any],
        *,
        options: RequestOptions | None = None,
    ) -> dict[str, Any]:
        chat_id = quote(_require(chat_id, "chat_id"), safe="")
        return self._transport.request(
            "PUT",
            f"v3/chats/{chat_id}",
            body=body,
            options=options,
        )

    def list(
        self,
        query: Mapping[str, Any] | None = None,
        *,
        options: RequestOptions | None = None,
    ) -> CursorPage[dict[str, Any]]:
        base_query = dict(query or {})

        def fetch(cursor: str) -> dict[str, Any]:
            next_query = dict(base_query)
            next_query["cursor"] = cursor
            return self._transport.request("GET", "v3/chats", query=next_query, options=options)

        payload = self._transport.request("GET", "v3/chats", query=base_query, options=options)
        return CursorPage(_item_key="chats", _payload=payload, _fetch_next=fetch)

    def list_auto_paging(
        self,
        query: Mapping[str, Any] | None = None,
        *,
        options: RequestOptions | None = None,
    ) -> AutoPager[dict[str, Any]]:
        return AutoPager(self.list(query, options=options))

    def mark_as_read(self, chat_id: str, *, options: RequestOptions | None = None) -> None:
        chat_id = quote(_require(chat_id, "chat_id"), safe="")
        options = merge_request_options(options, headers={"Accept": "*/*"})
        self._transport.request(
            "POST",
            f"v3/chats/{chat_id}/read",
            options=options,
            parse_json=False,
        )

    def send_voicememo(
        self,
        chat_id: str,
        body: Mapping[str, Any],
        *,
        options: RequestOptions | None = None,
    ) -> dict[str, Any]:
        chat_id = quote(_require(chat_id, "chat_id"), safe="")
        return self._transport.request(
            "POST",
            f"v3/chats/{chat_id}/voicememo",
            body=body,
            options=options,
        )

    def share_contact_card(self, chat_id: str, *, options: RequestOptions | None = None) -> None:
        chat_id = quote(_require(chat_id, "chat_id"), safe="")
        options = merge_request_options(options, headers={"Accept": "*/*"})
        self._transport.request(
            "POST",
            f"v3/chats/{chat_id}/share_contact_card",
            options=options,
            parse_json=False,
        )

    # Go-style aliases
    new = create
    list_chats = list
    list_chats_auto_paging = list_auto_paging
