# Alexa+ integration

The Alexa+ track asks for "a working MCP (Model Context Protocol) integration on
the open standards for Agent Skills and Streamable HTTP transports", and allows
simulating the Alexa+ experience via a web app. Recall does both.

## References (from the hackathon Resources page)
- Streamable HTTP transport spec **2025-11-25**:
  https://modelcontextprotocol.io/specification/2025-11-25/basic/transports#streamable-http
- Build with Agent Skills:
  https://apps.extensions.modelcontextprotocol.io/api/#build-with-agent-skills
- AWS credits ($150): https://forms.gle/GaHFxSbBQNG9Kti6A

## Two surfaces, one core

```
                    ┌───────────────────────────┐
 Alexa+  ──MCP──►   │  recall.server (FastMCP)   │
 (or MCP client)    │  Streamable HTTP  /mcp     │
                    └────────────┬──────────────┘
                                 │  core.py  (add / next / grade / progress)
                    ┌────────────┴──────────────┐
 Browser (voice) ─► │  recall.webapp (Starlette) │  ← Alexa+ experience simulator
                    │  /  + /api/*               │
                    └───────────────────────────┘
```

- **Track integration:** `recall.server` is the real MCP server. It speaks
  Streamable HTTP and negotiates protocol `2025-11-25` on `initialize`.
- **Demo experience:** `recall.webapp` is the permitted web-app simulation. It
  uses the browser Web Speech API (recognition + synthesis) for the hands-free
  loop and calls the same `core` operations, so what you see in the demo is the
  same logic Alexa+ drives.

## A. Connect an MCP client / Alexa+ to the server

1. Start the server:
   ```bash
   pip install -r requirements.txt
   python -m recall.server        # http://127.0.0.1:8000/mcp
   ```
2. Verify the transport and spec version:
   ```bash
   curl -s -X POST http://127.0.0.1:8000/mcp \
     -H "Content-Type: application/json" \
     -H "Accept: application/json, text/event-stream" \
     -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-11-25","capabilities":{},"clientInfo":{"name":"c","version":"0"}}}'
   # → result.protocolVersion == "2025-11-25"
   ```
3. Expose it over public HTTPS for a remote Alexa+ / MCP client (the transport
   requires it off-localhost). For the demo, any HTTPS tunnel works:
   ```bash
   # example: a tunnel to the local server
   <your-tunnel> http 8000        # publishes https://<id>/mcp
   ```
   Then register that `https://<host>/mcp` endpoint with your MCP client per the
   track's Agent Skills docs.

### Tools exposed
`add_source(text, topic, count)` · `next_review()` · `grade(card_id, answer)` ·
`progress()` — all return short, speakable output.

## B. Run the Alexa+ web simulator (demo)

```bash
python -m recall.webapp           # http://127.0.0.1:8080
# RECALL_WEB_PORT overrides the port
```
Open it in Chrome (best Web Speech API support), paste a source, click **Learn
this**, then **Quiz me** and answer out loud. This is the hands-free experience
the demo video shows.

## Notes
- Off-localhost, add auth in front of `/mcp` (a bearer token / reverse proxy).
  # ponytail: no auth on the demo server; add a token check before any public deploy.
- The web simulator needs a mic permission and, ideally, Chrome for
  `webkitSpeechRecognition`. If unavailable it degrades to typed answers.
