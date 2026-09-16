# Friction log

Submissions with a friction log can earn up to a 10% judging bonus. Each entry:
task attempted → steps → expected vs. actual → severity → workaround → suggestion.
Fill the `[verify]` marks against your own run before submitting; keep entries
honest and specific.

---

### 1. MCP Streamable HTTP — protocol version negotiation
- **Task:** Confirm the server advertises spec `2025-11-25` as the track requires.
- **Steps:** `python -m recall.server`, then a raw `initialize` POST to `/mcp`.
- **Expected:** Response echoes `protocolVersion: 2025-11-25`.
- **Actual:** Works — server returned `2025-11-25` over `text/event-stream`. The
  SDK negotiates down to the client's version, so an older client silently gets
  an older protocol with no warning.
- **Severity:** Low.
- **Workaround:** Pin the client's `protocolVersion` in the handshake and assert
  on it in CI.
- **Suggestion:** Surface a server-side log line when the negotiated version is
  below the configured minimum, so track-compliance regressions are visible.

### 2. Amazon Bedrock — Converse API JSON discipline
- **Task:** Get structured flashcards back from Claude via `converse`.
- **Steps:** Prompt for "ONLY a JSON array"; `json.loads` the response.
- **Expected:** Clean JSON.
- **Actual:** The model occasionally wraps JSON in prose or a ```` ```json ````
  fence, breaking a naive parse. `[verify against your model/region]`
- **Severity:** Medium — silent failures degrade to the offline fallback.
- **Workaround:** Regex-extract the first `[...]`/`{...}` block before parsing
  (see `bedrock._extract_json`).
- **Suggestion:** A first-class "response format = JSON" / tool-use enforced
  schema on Converse would remove this whole class of parsing glue.

### 3. Bedrock — model access gating per region
- **Task:** Call `anthropic.claude-3-5-sonnet` in `us-east-1`.
- **Steps:** First `converse` call on a fresh account.
- **Expected:** It just works with valid credentials.
- **Actual:** Model access must be explicitly enabled in the Bedrock console
  first, otherwise `AccessDeniedException`. `[verify on your account]`
- **Severity:** Medium — a confusing first-run blocker for newcomers.
- **Workaround:** Enable model access in console; the server's offline fallback
  keeps the demo alive until then.
- **Suggestion:** A clearer error that links straight to the model-access page,
  and a documented default of which models are pre-enabled for hackathon credits.

### 4. Local dev without an AWS account
- **Task:** Develop and test the SRS loop with no cloud credentials.
- **Expected:** Ability to iterate offline.
- **Actual:** Solved in-project — `bedrock.py` degrades to a deterministic
  keyword heuristic when boto3/credentials are absent, so `tests/test_flow.py`
  runs anywhere.
- **Severity:** Low (self-mitigated).
- **Suggestion:** An official Bedrock local emulator / recorded-response mode
  would make hackathon onboarding and CI dramatically smoother.
