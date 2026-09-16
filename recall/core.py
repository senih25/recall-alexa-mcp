"""Core learning operations, transport-agnostic.

Both surfaces call these: the MCP server (`server.py`, the Alexa+ track
integration) and the web simulator (`webapp.py`, the demo experience). Keeping
the logic here means the two never drift apart.
"""
from __future__ import annotations

import os

from .bedrock import generate_cards, grade_answer
from .srs import review
from .store import Card, Store

STORE = Store(os.getenv("RECALL_DB", "data/cards.json"))
USER = os.getenv("RECALL_USER", "default")


def add_source(text: str, topic: str, count: int = 5) -> dict:
    cards = generate_cards(text, topic, n=count)
    for c in cards:
        STORE.add(USER, Card(front=c["front"], back=c["back"], topic=topic))
    return {"added": len(cards), "say": f"Added {len(cards)} cards on {topic}. Say 'quiz me' when ready."}


def next_review() -> dict:
    due = STORE.due(USER)
    if not due:
        return {"done": True, "say": "Nothing due right now. Great job staying on top of it."}
    c = due[0]
    return {"done": False, "card_id": c.id, "topic": c.topic, "say": c.front}


def grade(card_id: str, answer: str) -> dict:
    card = next((c for c in STORE.cards(USER) if c.id == card_id), None)
    if card is None:
        return {"ok": False, "say": "I couldn't find that card."}
    result = grade_answer(card.front, card.back, answer)
    sched = review(result["grade"], card.repetitions, card.interval_days, card.easiness)
    card.repetitions = sched.repetitions
    card.interval_days = sched.interval_days
    card.easiness = sched.easiness
    card.due = sched.due.isoformat()
    STORE.update(USER, card)
    when = "tomorrow" if sched.interval_days == 1 else f"in {sched.interval_days} days"
    return {
        "ok": True,
        "grade": result["grade"],
        "say": f"{result['feedback']} The answer is: {card.back}. Next review {when}.",
    }


def progress() -> dict:
    cards = STORE.cards(USER)
    due = STORE.due(USER)
    learned = [c for c in cards if c.repetitions >= 3]
    return {
        "total": len(cards),
        "learned": len(learned),
        "due": len(due),
        "say": f"You have {len(cards)} cards, {len(learned)} well learned, and {len(due)} due for review.",
    }
