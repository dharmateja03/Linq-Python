from __future__ import annotations

import httpx
import pytest

from linq import APIError, Client, RequestOptions


def _sdk_client(handler, **kwargs):
    transport = httpx.MockTransport(handler)
    http_client = httpx.Client(base_url="https://api.linqapp.com/api/partner/", transport=transport)
    return Client(api_key="test_key", http_client=http_client, **kwargs)


def test_user_agent_header():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["ua"] = request.headers.get("User-Agent")
        return httpx.Response(200, json={"ok": True})

    client = _sdk_client(handler)
    client.chats.create({"from": "+1", "to": ["+2"], "message": {"parts": []}})

    assert seen["ua"].startswith("LinqAPIV3/Python ")


def test_retry_after_retries_three_attempts(monkeypatch):
    monkeypatch.setattr("linq._http.time.sleep", lambda _: None)

    retry_headers = []

    def handler(request: httpx.Request) -> httpx.Response:
        retry_headers.append(request.headers.get("X-Stainless-Retry-Count"))
        return httpx.Response(429, headers={"Retry-After": "0"}, json={"error": "rate_limited"})

    client = _sdk_client(handler, max_retries=2)

    with pytest.raises(APIError):
        client.chats.create({"from": "+1", "to": ["+2"], "message": {"parts": []}})

    assert retry_headers == ["0", "1", "2"]


def test_retry_after_ms_retries_three_attempts(monkeypatch):
    monkeypatch.setattr("linq._http.time.sleep", lambda _: None)

    attempts = 0

    def handler(_: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        return httpx.Response(429, headers={"Retry-After-Ms": "0"}, json={"error": "rate_limited"})

    client = _sdk_client(handler, max_retries=2)

    with pytest.raises(APIError):
        client.chats.create({"from": "+1", "to": ["+2"], "message": {"parts": []}})

    assert attempts == 3


def test_custom_http_client_without_base_url_still_uses_client_base_url():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["path"] = request.url.path
        return httpx.Response(200, json={"ok": True})

    # Intentionally no base_url on the provided client.
    http_client = httpx.Client(transport=httpx.MockTransport(handler))
    client = Client(
        api_key="test_key",
        base_url="https://api.linqapp.com/api/partner",
        http_client=http_client,
    )

    client.chats.create({"from": "+1", "to": ["+2"], "message": {"parts": []}})

    assert seen["path"] == "/api/partner/v3/chats"


def test_negative_retries_are_rejected():
    with pytest.raises(ValueError, match="max_retries cannot be negative"):
        Client(api_key="test_key", max_retries=-1)


def test_negative_request_retries_are_rejected():
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"ok": True})

    client = _sdk_client(handler)
    with pytest.raises(ValueError, match="max_retries cannot be negative"):
        client.chats.create(
            {"from": "+1", "to": ["+2"], "message": {"parts": []}},
            options=RequestOptions(max_retries=-1),
        )
