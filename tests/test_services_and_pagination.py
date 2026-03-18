from __future__ import annotations

import hashlib
import hmac
import json
import time

import httpx

from linq import Client


def _sdk_client(handler):
    transport = httpx.MockTransport(handler)
    http_client = httpx.Client(base_url="https://api.linqapp.com/api/partner/", transport=transport)
    return Client(api_key="test_key", http_client=http_client)


def test_chat_auto_paging_uses_cursor():
    seen_paths = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_paths.append(str(request.url))
        cursor = request.url.params.get("cursor")
        if cursor is None:
            return httpx.Response(200, json={"chats": [{"id": "c1"}], "next_cursor": "n1"})
        return httpx.Response(200, json={"chats": [{"id": "c2"}], "next_cursor": None})

    client = _sdk_client(handler)

    items = list(client.chats.list_auto_paging({"limit": 1}))

    assert [item["id"] for item in items] == ["c1", "c2"]
    assert any("cursor=n1" in path for path in seen_paths)


def test_service_paths_and_methods():
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append((request.method, request.url.path))
        if request.method == "DELETE":
            return httpx.Response(204)
        return httpx.Response(200, json={"ok": True})

    client = _sdk_client(handler)

    client.chats.get("chat_1")
    client.messages.update("msg_1", {"part_index": 0, "value": "updated"})
    client.attachments.get("att_1")
    client.webhook_events.list()
    client.webhook_subscriptions.delete("sub_1")
    client.capability.check_imessage({"address": "+12223334444"})

    assert ("GET", "/api/partner/v3/chats/chat_1") in calls
    assert ("PATCH", "/api/partner/v3/messages/msg_1") in calls
    assert ("GET", "/api/partner/v3/attachments/att_1") in calls
    assert ("GET", "/api/partner/v3/webhook-events") in calls
    assert ("DELETE", "/api/partner/v3/webhook-subscriptions/sub_1") in calls
    assert ("POST", "/api/partner/v3/capability/check_imessage") in calls


def test_webhook_signature_verification():
    client = Client(api_key="test_key")

    payload = json.dumps({"event": "message.sent"}, separators=(",", ":")).encode("utf-8")
    timestamp = str(int(time.time()))
    secret = "whsec_test"

    message = f"{timestamp}.".encode() + payload
    signature = hmac.new(secret.encode("utf-8"), message, hashlib.sha256).hexdigest()

    assert client.webhooks.verify_signature(secret, payload, timestamp, signature)
    assert not client.webhooks.verify_signature(secret, payload, timestamp, "bad-signature")
