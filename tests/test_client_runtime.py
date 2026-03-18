from __future__ import annotations

import httpx
import pytest

from linq import APIError, Client


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
