from __future__ import annotations

from collections.abc import Callable, Iterator
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

T = TypeVar("T")


@dataclass(slots=True)
class CursorPage(Generic[T]):
    """Cursor-based pagination wrapper."""

    _item_key: str
    _payload: dict[str, Any]
    _fetch_next: Callable[[str], dict[str, Any]]

    @property
    def raw(self) -> dict[str, Any]:
        return self._payload

    @property
    def items(self) -> list[T]:
        value = self._payload.get(self._item_key)
        if isinstance(value, list):
            return value
        return []

    @property
    def next_cursor(self) -> str | None:
        cursor = self._payload.get("next_cursor")
        if cursor in (None, ""):
            return None
        return str(cursor)

    def get_next_page(self) -> CursorPage[T] | None:
        cursor = self.next_cursor
        if not cursor:
            return None
        return CursorPage(
            _item_key=self._item_key,
            _payload=self._fetch_next(cursor),
            _fetch_next=self._fetch_next,
        )


class AutoPager(Iterator[T], Generic[T]):
    """Iterator that keeps fetching cursor pages until exhausted."""

    def __init__(self, page: CursorPage[T] | None):
        self._page = page
        self._index = 0

    def __iter__(self) -> AutoPager[T]:
        return self

    def __next__(self) -> T:
        while self._page is not None:
            items = self._page.items
            if self._index < len(items):
                item = items[self._index]
                self._index += 1
                return item

            self._page = self._page.get_next_page()
            self._index = 0

        raise StopIteration
