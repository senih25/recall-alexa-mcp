"""AWS Bedrock (Claude) wrapper for generating cards and grading answers.

Satisfies the AWS Builder mini challenge: the server calls Bedrock's
Converse API for both flashcard generation and free-text answer grading.

If AWS credentials are absent (local dev, CI), falls back to a deterministic
heuristic so the server still runs and the SRS loop can be demoed without a
cloud account.
"""
from __future__ import annotations

import json
import os
import re

MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0")
REGION = os.getenv("AWS_REGION", "us-east-1")


def _client():
    try:
        import boto3

        return boto3.client("bedrock-runtime", region_name=REGION)
    except Exception:
        return None


def _converse(client, prompt: str, max_tokens: int = 1024) -> str:
    resp = client.converse(
        modelId=MODEL_ID,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={"maxTokens": max_tokens, "temperature": 0.2},
    )
    return resp["output"]["message"]["content"][0]["text"]


def generate_cards(source: str, topic: str, n: int = 5) -> list[dict]:
    """Turn a chunk of source text into up to n Q/A flashcards."""
    client = _client()
    if client is None:
        return _fallback_cards(source, topic, n)

    prompt = (
        f"Create {n} spaced-repetition flashcards on the topic '{topic}' from the "
        f"text below. Each card: one focused question and a concise, correct answer. "
        f"Return ONLY a JSON array of objects with keys 'front' and 'back'.\n\n{source}"
    )
    try:
        text = _converse(client, prompt)
        cards = json.loads(_extract_json(text))
        return [{"front": c["front"], "back": c["back"]} for c in cards][:n]
    except Exception:
        return _fallback_cards(source, topic, n)


def grade_answer(question: str, correct: str, user_answer: str) -> dict:
    """Grade a spoken answer against the reference. Returns {grade 0-5, feedback}."""
    client = _client()
    if client is None:
        return _fallback_grade(correct, user_answer)

    prompt = (
        "You grade a learner's spoken answer for a spaced-repetition system.\n"
        f"Question: {question}\nReference answer: {correct}\n"
        f"Learner answer: {user_answer}\n\n"
        "Return ONLY JSON {\"grade\": <0-5 integer>, \"feedback\": <one short sentence>}. "
        "5 = perfect, 3 = correct with hesitation/gaps, 0-2 = incorrect or forgotten."
    )
    try:
        text = _converse(client, prompt, max_tokens=256)
        out = json.loads(_extract_json(text))
        return {"grade": max(0, min(5, int(out["grade"]))), "feedback": str(out["feedback"])}
    except Exception:
        return _fallback_grade(correct, user_answer)


def _extract_json(text: str) -> str:
    m = re.search(r"(\[.*\]|\{.*\})", text, re.DOTALL)
    return m.group(1) if m else text


def _fallback_cards(source: str, topic: str, n: int) -> list[dict]:
    sents = [s.strip() for s in re.split(r"[.\n]", source) if len(s.strip()) > 20]
    cards = []
    for s in sents[:n]:
        cards.append({"front": f"Recall this fact about {topic}: …?", "back": s})
    return cards or [{"front": f"What is {topic}?", "back": source[:200].strip()}]


def _fallback_grade(correct: str, user_answer: str) -> dict:
    ca = set(re.findall(r"\w+", correct.lower()))
    ua = set(re.findall(r"\w+", user_answer.lower()))
    if not ca:
        return {"grade": 3, "feedback": "No reference to compare against."}
    overlap = len(ca & ua) / len(ca)
    grade = round(overlap * 5)
    return {"grade": grade, "feedback": f"Keyword overlap {overlap:.0%} (offline heuristic)."}


def _demo() -> None:
    # Offline path must always produce usable output.
    cards = generate_cards(
        "MCP is the Model Context Protocol. It standardises tool access for agents.",
        "mcp",
        n=2,
    )
    assert cards and all("front" in c and "back" in c for c in cards), cards
    g = grade_answer("What is MCP?", "Model Context Protocol", "the model context protocol")
    assert 0 <= g["grade"] <= 5, g
    assert g["grade"] >= 3, g  # strong overlap should pass
    print("bedrock self-check ok (offline fallback)")


if __name__ == "__main__":
    _demo()
