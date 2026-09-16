"""Alexa+ experience simulator (web app).

The hackathon Alexa+ track explicitly allows simulating the Alexa+ experience
"using your preferred agentic tools via a web app". This serves a voice-driven
page (browser Web Speech API) backed by the same `core` operations the MCP
server exposes, so the demo shows a real hands-free loop.

Run:  python -m recall.webapp          # http://127.0.0.1:8080
"""
from __future__ import annotations

from pathlib import Path

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse
from starlette.routing import Route

from . import core

WEB = Path(__file__).resolve().parent.parent / "web"


async def index(_: Request):
    return FileResponse(WEB / "index.html")


async def api_add(req: Request):
    b = await req.json()
    return JSONResponse(core.add_source(b["text"], b.get("topic", "general"), int(b.get("count", 5))))


async def api_next(_: Request):
    return JSONResponse(core.next_review())


async def api_grade(req: Request):
    b = await req.json()
    return JSONResponse(core.grade(b["card_id"], b["answer"]))


async def api_progress(_: Request):
    return JSONResponse(core.progress())


app = Starlette(
    routes=[
        Route("/", index),
        Route("/api/add", api_add, methods=["POST"]),
        Route("/api/next", api_next, methods=["POST"]),
        Route("/api/grade", api_grade, methods=["POST"]),
        Route("/api/progress", api_progress, methods=["POST"]),
    ]
)


def main() -> None:
    import os

    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=int(os.getenv("RECALL_WEB_PORT", "8080")))


if __name__ == "__main__":
    main()
