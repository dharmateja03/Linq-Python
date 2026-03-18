from __future__ import annotations

import os
from collections.abc import Mapping
from typing import Any

import httpx

from ._http import HTTPTransport
from ._request_options import RequestOptions
from .services import (
    AttachmentsService,
    CapabilityService,
    ChatsService,
    MessagesService,
    PhoneNumbersService,
    PhonenumbersService,
    WebhookEventsService,
    WebhooksService,
    WebhookSubscriptionsService,
)

DEFAULT_BASE_URL = "https://api.linqapp.com/api/partner/"


class Client:
    """Linq API v3 client."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        max_retries: int = 2,
        timeout: float | None = 60.0,
        http_client: httpx.Client | None = None,
        default_headers: Mapping[str, str] | None = None,
    ) -> None:
        api_key = api_key or os.getenv("LINQ_API_V3_API_KEY")
        base_url = base_url or os.getenv("LINQ_API_V3_BASE_URL") or DEFAULT_BASE_URL

        self._transport = HTTPTransport(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            http_client=http_client,
            default_headers=default_headers,
        )

        self.chats = ChatsService(self._transport)
        self.messages = MessagesService(self._transport)
        self.attachments = AttachmentsService(self._transport)
        self.phonenumbers = PhonenumbersService(self._transport)
        self.phone_numbers = PhoneNumbersService(self._transport)
        self.webhook_events = WebhookEventsService(self._transport)
        self.webhook_subscriptions = WebhookSubscriptionsService(self._transport)
        self.capability = CapabilityService(self._transport)
        self.webhooks = WebhooksService()

        # Go-style aliases
        self.Chats = self.chats
        self.Messages = self.messages
        self.Attachments = self.attachments
        self.Phonenumbers = self.phonenumbers
        self.PhoneNumbers = self.phone_numbers
        self.WebhookEvents = self.webhook_events
        self.WebhookSubscriptions = self.webhook_subscriptions
        self.Capability = self.capability
        self.Webhooks = self.webhooks

    def close(self) -> None:
        self._transport.close()

    def __enter__(self) -> Client:
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        self.close()

    def execute(
        self,
        method: str,
        path: str,
        *,
        params: Any | None = None,
        query: Mapping[str, Any] | None = None,
        options: RequestOptions | None = None,
        parse_json: bool = True,
    ) -> Any:
        return self._transport.request(
            method,
            path,
            body=params,
            query=query,
            options=options,
            parse_json=parse_json,
        )

    def get(
        self,
        path: str,
        *,
        query: Mapping[str, Any] | None = None,
        options: RequestOptions | None = None,
        parse_json: bool = True,
    ) -> Any:
        return self.execute("GET", path, query=query, options=options, parse_json=parse_json)

    def post(
        self,
        path: str,
        *,
        params: Any | None = None,
        query: Mapping[str, Any] | None = None,
        options: RequestOptions | None = None,
        parse_json: bool = True,
    ) -> Any:
        return self.execute(
            "POST",
            path,
            params=params,
            query=query,
            options=options,
            parse_json=parse_json,
        )

    def put(
        self,
        path: str,
        *,
        params: Any | None = None,
        query: Mapping[str, Any] | None = None,
        options: RequestOptions | None = None,
        parse_json: bool = True,
    ) -> Any:
        return self.execute(
            "PUT",
            path,
            params=params,
            query=query,
            options=options,
            parse_json=parse_json,
        )

    def patch(
        self,
        path: str,
        *,
        params: Any | None = None,
        query: Mapping[str, Any] | None = None,
        options: RequestOptions | None = None,
        parse_json: bool = True,
    ) -> Any:
        return self.execute(
            "PATCH",
            path,
            params=params,
            query=query,
            options=options,
            parse_json=parse_json,
        )

    def delete(
        self,
        path: str,
        *,
        params: Any | None = None,
        query: Mapping[str, Any] | None = None,
        options: RequestOptions | None = None,
        parse_json: bool = True,
    ) -> Any:
        return self.execute(
            "DELETE",
            path,
            params=params,
            query=query,
            options=options,
            parse_json=parse_json,
        )
