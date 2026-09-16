"""End-to-end flow check: add cards -> review -> grade -> reschedule.

Runs against the offline Bedrock fallback so it needs no AWS account.
"""
import os
import tempfile

os.environ["RECALL_DB"] = os.path.join(tempfile.mkdtemp(), "cards.json")
os.environ["RECALL_USER"] = "tester"

from recall import server  # noqa: E402  (env must be set before import)


def test_full_loop():
    msg = server.add_source(
        "MCP is the Model Context Protocol. It standardises how agents reach tools. "
        "Streamable HTTP is its remote transport.",
        topic="mcp",
        count=3,
    )
    assert "Added" in msg

    nxt = server.next_review()
    assert nxt["done"] is False
    assert nxt["card_id"] and nxt["say"]

    before_due = server.progress()["due"]
    out = server.grade(nxt["card_id"], "the model context protocol")
    assert "Next review" in out

    # Grading a card pushes its due date out, so fewer cards are due now.
    assert server.progress()["due"] < before_due

    # Unknown card id is handled gracefully.
    assert "couldn't find" in server.grade("nope", "x")

    print("flow self-check ok")


if __name__ == "__main__":
    test_full_loop()
