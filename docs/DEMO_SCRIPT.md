# Demo video script — under 3 minutes

Judges may stop at 3:00, so the hook and a working demo come first; context
comes after. Target run time **2:45**. Public, English, YouTube/Vimeo.

## 0:00–0:20 — Hook (lead with the pain)
> "I finished twelve courses last month. A week later, most of it was gone.
> Reading isn't remembering. Recall turns anything you read into a hands-free
> quiz on Alexa+, so it actually sticks."

On screen: title card → the phrase "Reading ≠ Remembering" → Recall logo.

## 0:20–0:45 — What it is (one sentence + architecture beat)
> "Recall is a self-hosted MCP server. Alexa+ talks to it over Streamable HTTP.
> Amazon Bedrock turns my notes into flashcards and grades my spoken answers,
> and an SM-2 scheduler decides what I review and when."

On screen: the README architecture diagram, 4 seconds.

## 0:45–1:30 — Demo part 1: capture
- Show a real source (e.g. Kubernetes docs paragraph) pasted into the client.
- Voice: *"Alexa, ask Recall to learn this."* → tool call `add_source`.
- Cut to server logs showing the Bedrock Converse call and "Added 5 cards."

## 1:30–2:20 — Demo part 2: hands-free review (the money shot)
- Voice: *"Alexa, ask Recall to quiz me."* → `next_review` speaks a question.
- Answer **out loud, imperfectly** → `grade` returns Bedrock feedback + the
  correct answer + "Next review in 6 days."
- Do one more card, answer wrong on purpose → show the lapse resets it to
  "tomorrow." This proves the SM-2 logic is real, not a gimmick.
- Voice: *"Alexa, ask Recall how I'm doing."* → `progress` speaks the recap.

## 2:20–2:45 — Impact + close
> "Every commute, every dish washed, becomes a review session — no screen.
> It's open source, it runs on Bedrock, and it's built on the open MCP standard
> that powers Alexa+. This is how learning should feel."

On screen: GitHub URL, MIT badge, "Alexa+ · AWS Builder · Open Source."

## Shot list / prep
- [ ] Screen recording of the MCP client + server logs side by side.
- [ ] Clean audio for the voice lines (record separately, overlay).
- [ ] Pre-seed one topic so `progress` shows real numbers.
- [ ] Show the `initialize` response with `protocolVersion 2025-11-25` for 2s
      (proves the spec requirement on camera).
- [ ] No third-party music/footage without rights (use silence or CC-0).
