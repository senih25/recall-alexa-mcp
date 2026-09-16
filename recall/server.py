"""Recall — a hands-free spaced-repetition learning coach exposed as an
MCP server over Streamable HTTP, for the Alexa+ track.

Tools are written to be *spoken*: every response is a short string Alexa+ can
read aloud. Bedrock does card generation and answer grading (AWS Builder mini);
an SM-2 scheduler decides what to review and when.

Run:  python -m recall.server         # Streamable HTTP on :8000/mcp
"""
from __future__ import annotations

import os
from datetime import date

from mcp.server.fastmcp import FastMCP

from .bedrock import generate_cards, grade_answer
from .srs import review
from .store import Card, Store

STORE = Store(os.getenv("RECALL_DB", "data/cards.json"))
# Single-tenant demo default. A real deployment maps this to the Alexa+ user.
USER = os.getenv("RECALL_USER", "default")

mcp = FastMCP("recall", stateless_http=True)


@mcp.tool()
def add_source(text: str, topic: str, count: int = 5) -> str:
    """Create flashcards from a chunk of text (notes, docs, an article) on a topic."""
    cards = generate_cards(text, topic, n=count)
    for c in cards:
        STORE.add(USER, Card(front=c["front"], back=c["back"], topic=topic))
    return f"Added {len(cards)} cards on {topic}. Say 'quiz me' when you're ready."


@mcp.tool()
def next_review() -> dict:
    """Get the next card due for review. Returns its id and question to read aloud."""
    due = STORE.due(USER)
    if not due:
        return {"done": True, "say": "Nothing due right now. Great job staying on top of it."}
    c = due[0]
    return {"done": False, "card_id": c.id, "topic": c.topic, "say": c.front}


@mcp.tool()
def grade(card_id: str, answer: str) -> str:
    """Grade the learner's spoken answer and schedule the next review (SM-2)."""
    card = next((c for c in STORE.cards(USER) if c.id == card_id), None)
    if card is None:
        return "I couldn't find that card."
    result = grade_answer(card.front, card.back, answer)
    sched = review(result["grade"], card.repetitions, card.interval_days, card.easiness)
    card.repetitions = sched.repetitions
    card.interval_days = sched.interval_days
    card.easiness = sched.easiness
    card.due = sched.due.isoformat()
    STORE.update(USER, card)
    when = "tomorrow" if sched.interval_days == 1 else f"in {sched.interval_days} days"
    return f"{result['feedback']} The answer is: {card.back}. Next review {when}."


@mcp.tool()
def progress() -> dict:
    """Summarise how many cards are learned, due, and total — for a spoken recap."""
    cards = STORE.cards(USER)
    due = STORE.due(USER)
    learned = [c for c in cards if c.repetitions >= 3]
    say = (
        f"You have {len(cards)} cards, {len(learned)} well learned, "
        f"and {len(due)} due for review."
    )
    return {"total": len(cards), "learned": len(learned), "due": len(due), "say": say}


def main() -> None:
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
