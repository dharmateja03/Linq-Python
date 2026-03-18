from __future__ import annotations

from collections.abc import Mapping
from typing import Any
from urllib.parse import quote

from .._http import HTTPTransport
from .._request_options import RequestOptions, merge_request_options


def _require(value: str, name: str) -> str:
    if not value:
        raise ValueError(f"missing required {name} parameter")
    return value


class WebhookSubscriptionsService:
    def __init__(self, transport: HTTPTransport) -> None:
        self._transport = transport

    def create(
        self,
        body: Mapping[str, Any],
        *,
        options: RequestOptions | None = None,
    ) -> dict[str, Any]:
        return self._transport.request(
            "POST",
            "v3/webhook-subscriptions",
            body=body,
            options=options,
        )

    def get(
        self,
        subscription_id: str,
        *,
        options: RequestOptions | None = None,
    ) -> dict[str, Any]:
        subscription_id = quote(_require(subscription_id, "subscription_id"), safe="")
        return self._transport.request(
            "GET",
            f"v3/webhook-subscriptions/{subscription_id}",
            options=options,
        )

    def update(
        self,
        subscription_id: str,
        body: Mapping[str, Any],
        *,
        options: RequestOptions | None = None,
    ) -> dict[str, Any]:
        subscription_id = quote(_require(subscription_id, "subscription_id"), safe="")
        return self._transport.request(
            "PUT",
            f"v3/webhook-subscriptions/{subscription_id}",
            body=body,
            options=options,
        )

    def list(self, *, options: RequestOptions | None = None) -> dict[str, Any]:
        return self._transport.request("GET", "v3/webhook-subscriptions", options=options)

    def delete(self, subscription_id: str, *, options: RequestOptions | None = None) -> None:
        subscription_id = quote(_require(subscription_id, "subscription_id"), safe="")
        options = merge_request_options(options, headers={"Accept": "*/*"})
        self._transport.request(
            "DELETE",
            f"v3/webhook-subscriptions/{subscription_id}",
            options=options,
            parse_json=False,
        )

    # Go-style alias
    new = create
