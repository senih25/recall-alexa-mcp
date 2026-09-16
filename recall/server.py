"""Recall — a hands-free spaced-repetition learning coach exposed as an
MCP server over Streamable HTTP, for the Alexa+ track.

Tools return short, speakable strings Alexa+ can read aloud. The learning logic
lives in `core.py`; this module only adapts it to MCP.

Run:  python -m recall.server         # Streamable HTTP on :8000/mcp
"""
from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from . import core

mcp = FastMCP("recall", stateless_http=True)


@mcp.tool()
def add_source(text: str, topic: str, count: int = 5) -> str:
    """Create flashcards from a chunk of text (notes, docs, an article) on a topic."""
    return core.add_source(text, topic, count)["say"]


@mcp.tool()
def next_review() -> dict:
    """Get the next card due for review. Returns its id and question to read aloud."""
    return core.next_review()


@mcp.tool()
def grade(card_id: str, answer: str) -> str:
    """Grade the learner's spoken answer and schedule the next review (SM-2)."""
    return core.grade(card_id, answer)["say"]


@mcp.tool()
def progress() -> dict:
    """Summarise how many cards are learned, due, and total — for a spoken recap."""
    return core.progress()


def main() -> None:
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
