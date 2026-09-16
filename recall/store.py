"""Card persistence.

JSON file keyed by user id. Fine for a single-node self-hosted server and
the hackathon demo.
# ponytail: single JSON file + process lock, swap for DynamoDB if multi-user
# concurrency ever matters.
"""
from __future__ import annotations

import json
import threading
import uuid
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path

_LOCK = threading.Lock()


@dataclass
class Card:
    front: str
    back: str
    topic: str
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    repetitions: int = 0
    interval_days: int = 0
    easiness: float = 2.5
    due: str = field(default_factory=lambda: date.today().isoformat())


class Store:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self._data: dict[str, list[dict]] = {}
        if self.path.exists():
            self._data = json.loads(self.path.read_text("utf-8"))

    def _flush(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self._data, indent=2), "utf-8")

    def add(self, user: str, card: Card) -> Card:
        with _LOCK:
            self._data.setdefault(user, []).append(asdict(card))
            self._flush()
        return card

    def cards(self, user: str) -> list[Card]:
        return [Card(**c) for c in self._data.get(user, [])]

    def due(self, user: str, today: date | None = None) -> list[Card]:
        today = today or date.today()
        return [c for c in self.cards(user) if date.fromisoformat(c.due) <= today]

    def update(self, user: str, card: Card) -> None:
        with _LOCK:
            rows = self._data.get(user, [])
            for i, c in enumerate(rows):
                if c["id"] == card.id:
                    rows[i] = asdict(card)
                    self._flush()
                    return
            raise KeyError(card.id)


def _demo() -> None:
    import tempfile

    p = Path(tempfile.mkdtemp()) / "cards.json"
    s = Store(p)
    c = s.add("u1", Card(front="What is MCP?", back="Model Context Protocol", topic="ai"))
    assert len(s.cards("u1")) == 1
    assert len(s.due("u1")) == 1  # new card due today
    c.due = "2999-01-01"
    s.update("u1", c)
    assert len(s.due("u1")) == 0  # pushed into the future
    assert len(Store(p).cards("u1")) == 1  # survived a reload
    print("store self-check ok")


if __name__ == "__main__":
    _demo()
