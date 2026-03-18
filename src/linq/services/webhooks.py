from __future__ import annotations

import hashlib
import hmac
import json
import time
from collections.abc import Mapping
from typing import Any


def _payload_to_bytes(payload: bytes | str | Mapping[str, Any]) -> bytes:
    if isinstance(payload, bytes):
        return payload
    if isinstance(payload, str):
        return payload.encode("utf-8")
    return json.dumps(payload, separators=(",", ":")).encode("utf-8")


class WebhooksService:
    """Utilities for webhook payload parsing and signature verification."""

    def events(self, payload: bytes | str | Mapping[str, Any]) -> dict[str, Any]:
        if isinstance(payload, dict):
            return dict(payload)
        raw = _payload_to_bytes(payload)
        return json.loads(raw.decode("utf-8"))

    def verify_signature(
        self,
        signing_secret: str,
        payload: bytes | str | Mapping[str, Any],
        timestamp: str,
        signature: str,
        *,
        max_age_seconds: int | None = 300,
    ) -> bool:
        if max_age_seconds is not None:
            try:
                ts = int(timestamp)
            except ValueError:
                return False

            if abs(int(time.time()) - ts) > max_age_seconds:
                return False

        payload_bytes = _payload_to_bytes(payload)
        message = f"{timestamp}.".encode() + payload_bytes

        expected = hmac.new(
            signing_secret.encode("utf-8"),
            message,
            hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(expected, signature)

    def verify_headers(
        self,
        signing_secret: str,
        payload: bytes | str | Mapping[str, Any],
        headers: Mapping[str, str],
        *,
        max_age_seconds: int | None = 300,
    ) -> bool:
        normalized_headers = {str(k).lower(): str(v) for k, v in headers.items()}

        timestamp = normalized_headers.get("x-webhook-timestamp", "")
        signature = normalized_headers.get("x-webhook-signature", "")
        if not timestamp or not signature:
            return False
        return self.verify_signature(
            signing_secret,
            payload,
            timestamp,
            signature,
            max_age_seconds=max_age_seconds,
        )
