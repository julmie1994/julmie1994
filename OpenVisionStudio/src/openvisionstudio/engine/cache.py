from dataclasses import dataclass, field
from typing import Any


@dataclass
class CacheEntry:
    signature: str
    outputs: dict[str, Any]


@dataclass
class NodeCache:
    _entries: dict[str, CacheEntry] = field(default_factory=dict)

    def get(self, node_id: str, signature: str) -> dict[str, Any] | None:
        entry = self._entries.get(node_id)
        if not entry or entry.signature != signature:
            return None
        return entry.outputs

    def put(self, node_id: str, signature: str, outputs: dict[str, Any]) -> None:
        self._entries[node_id] = CacheEntry(signature=signature, outputs=outputs)

    def invalidate(self, node_id: str) -> None:
        self._entries.pop(node_id, None)

    def clear(self) -> None:
        self._entries.clear()
