from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class RequestOptions:
    """Per-request overrides for SDK calls."""

    headers: Mapping[str, str] | None = None
    query: Mapping[str, Any] | None = None
    timeout: float | None = None
    max_retries: int | None = None
    raw_body: bytes | str | None = None
    content_type: str | None = None


def merge_request_options(
    base: RequestOptions | None,
    *,
    headers: Mapping[str, str] | None = None,
) -> RequestOptions | None:
    """Return merged options while preserving existing values."""

    if base is None and not headers:
        return None

    merged_headers: dict[str, str] = {}
    if base and base.headers:
        merged_headers.update(base.headers)
    if headers:
        merged_headers.update(headers)

    return RequestOptions(
        headers=merged_headers or None,
        query=base.query if base else None,
        timeout=base.timeout if base else None,
        max_retries=base.max_retries if base else None,
        raw_body=base.raw_body if base else None,
        content_type=base.content_type if base else None,
    )
