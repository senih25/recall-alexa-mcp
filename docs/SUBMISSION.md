# Devpost submission draft

Paste these into the Devpost submission form fields. Replace every `<…>` before
submitting.

## Project name
Recall — hands-free spaced-repetition learning coach for Alexa+

## Elevator pitch (one line)
Turn anything you read into a voice-quizzed habit: Recall builds flashcards with
Amazon Bedrock and coaches you hands-free through Alexa+ on an SM-2 schedule.

## Tracks & mini challenges
- **Primary track:** Alexa+
- **Mini challenges:** AWS Builder · Open Source

## What it does / how it works (description)
Recall is a self-hosted **MCP server** (Streamable HTTP, spec 2025-11-25) that
gives Alexa+ four tools: `add_source`, `next_review`, `grade`, and `progress`.
You feed it a source — notes, docs, an article — and **Amazon Bedrock** (Claude,
Converse API) turns it into focused flashcards. When you say "quiz me", Alexa+
reads a question aloud; you answer by voice; Bedrock grades the answer and an
**SM-2 spaced-repetition scheduler** decides when that card comes back. Hard
cards resurface soon, mastered cards fade out — so review time goes where it's
needed. A web app simulates the Alexa+ experience for the demo using the browser
Web Speech API, backed by the exact same core logic.

## Required tech, called in code
- **Alexa+ / MCP:** `recall/server.py` runs a FastMCP server on `streamable-http`;
  `initialize` returns `protocolVersion 2025-11-25`.
- **AWS (Bedrock):** `recall/bedrock.py` calls `bedrock-runtime.converse` for card
  generation and answer grading.

## Built during the hackathon window
Entire project built during the submission window: MCP server, SM-2 scheduler,
Bedrock integration, JSON store, Alexa+ web simulator, tests, and docs. No
pre-existing code.

## Product feedback (required)
See `docs/FRICTION_LOG.md` for the full friction log (eligible for the up-to-10%
bonus). Summary of tools used:
- **MCP Python SDK / FastMCP** — Streamable HTTP worked out of the box; protocol
  negotiation is silent (see friction #1). Would build with it again.
- **Amazon Bedrock Converse** — clean API; needs per-region model access enabled
  first (friction #3) and stricter JSON output enforcement (friction #2).
- **AWS credits** — requested via the hackathon form.

## Open Source mini — required fields
- **Repo URL:** `<https://github.com/<you>/recall-alexa-mcp>`
- **License:** MIT (`LICENSE`, visible in repo About)
- **GitHub username:** `<your-username>`
- **What / how / why:** New, standalone MIT-licensed project created during the
  window: an MCP server + Alexa+ simulator for spaced-repetition learning. It
  matters because it makes any Alexa+ device a hands-free study coach built on
  the open MCP standard.

## AWS Builder mini — required fields
- **AWS services used:** Amazon Bedrock (Converse API; Claude 3.5 Sonnet).
- **How:** Flashcard generation from source text and grading of free-text spoken
  answers; see `recall/bedrock.py`.

## Demo video
`<YouTube/Vimeo URL, < 3 min, public, English>` — storyboard in
`docs/DEMO_SCRIPT.md`.

## Repo
`<https://github.com/<you>/recall-alexa-mcp>`
