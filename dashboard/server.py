"""
Explieo Agent Orchestrator Monitor — FastAPI Backend
"""
import asyncio
import re
import time
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from parser import list_runs, parse_run

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
PROJECT_DIR = BASE_DIR.parent
RUNS_DIR = PROJECT_DIR / ".github" / "agent-workflow" / "runs"

# ─── WebSocket Manager ────────────────────────────────────────────────────────

class ConnectionManager:
    def __init__(self):
        self._connections = []

    async def connect(self, ws):
        await ws.accept()
        self._connections.append(ws)

    def disconnect(self, ws):
        self._connections = [c for c in self._connections if c is not ws]

    async def broadcast(self, payload):
        dead = []
        for ws in self._connections:
            try:
                await ws.send_json(payload)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)

    @property
    def count(self):
        return len(self._connections)


manager = ConnectionManager()

# ─── File Watcher ─────────────────────────────────────────────────────────────
# The watchdog handler runs in a background thread.
# We must use call_soon_threadsafe to safely hand events to the asyncio loop.

_DEBOUNCE = 0.8  # seconds — ignore repeated events for the same path
_debounce_times = {}


class RunsFileHandler(FileSystemEventHandler):
    """Watchdog handler that posts events into an asyncio Queue thread-safely."""

    def __init__(self, loop, queue):
        super().__init__()
        self._loop = loop
        self._queue = queue

    def _enqueue(self, event_type, path):
        now = time.monotonic()
        if now - _debounce_times.get(path, 0) < _DEBOUNCE:
            return
        _debounce_times[path] = now

        payload = {"type": event_type, "path": path, "ts": datetime.now().isoformat()}

        # Thread-safe: schedule a put_nowait on the event loop
        def _put():
            try:
                self._queue.put_nowait(payload)
            except asyncio.QueueFull:
                pass  # drop rather than block

        self._loop.call_soon_threadsafe(_put)

    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith(".md"):
            self._enqueue("file_modified", event.src_path)

    def on_created(self, event):
        if event.is_directory:
            self._enqueue("run_created", event.src_path)
        elif event.src_path.endswith(".md"):
            self._enqueue("file_created", event.src_path)

    def on_deleted(self, event):
        if event.is_directory:
            self._enqueue("run_deleted", event.src_path)


# ─── Event Processor ──────────────────────────────────────────────────────────

async def _event_processor(queue):
    """Read from queue (created on the running loop) and broadcast via WebSocket."""
    while True:
        try:
            event = await asyncio.wait_for(queue.get(), timeout=2.0)
        except asyncio.TimeoutError:
            continue
        except asyncio.CancelledError:
            break
        except Exception:
            await asyncio.sleep(0.5)
            continue

        try:
            path = Path(event["path"])

            # Which run does this file belong to?
            run_name = None
            for parent in path.parents:
                if parent.parent == RUNS_DIR:
                    run_name = parent.name
                    break

            payload = {"type": "update", "event": event, "run_name": run_name}

            if run_name:
                run_path = RUNS_DIR / run_name
                if run_path.exists():
                    try:
                        payload["run"] = parse_run(run_path)
                    except Exception as e:
                        payload["parse_error"] = str(e)

            try:
                payload["runs_list"] = list_runs(RUNS_DIR)
            except Exception:
                pass

            await manager.broadcast(payload)

        except Exception as e:
            print(f"[monitor] broadcast error: {e}")


# ─── App Lifecycle ────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app):
    # Create queue INSIDE the running event loop (Python 3.8 requirement)
    queue = asyncio.Queue(maxsize=100)

    loop = asyncio.get_event_loop()
    RUNS_DIR.mkdir(parents=True, exist_ok=True)

    observer = Observer()
    observer.schedule(RunsFileHandler(loop, queue), str(RUNS_DIR), recursive=True)
    observer.start()

    processor = asyncio.ensure_future(_event_processor(queue))

    print(f"\n  Explieo Agent Monitor")
    print(f"  Dashboard : http://localhost:8765")
    print(f"  Watching  : {RUNS_DIR}\n")

    yield

    processor.cancel()
    try:
        await processor
    except asyncio.CancelledError:
        pass
    observer.stop()
    observer.join()


app = FastAPI(title="Explieo Agent Monitor", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── REST API ─────────────────────────────────────────────────────────────────

@app.get("/api/runs")
async def api_list_runs():
    return list_runs(RUNS_DIR)


@app.get("/api/runs/{run_name}")
async def api_get_run(run_name: str):
    run_path = RUNS_DIR / run_name
    if not run_path.exists():
        return JSONResponse({"error": "Run not found"}, status_code=404)
    return parse_run(run_path)


@app.get("/api/runs/{run_name}/file/{file_stem}")
async def api_get_file(run_name: str, file_stem: str):
    if not re.match(r'^[\w\-]+$', run_name) or not re.match(r'^[\w\-]+$', file_stem):
        return JSONResponse({"error": "Invalid name"}, status_code=400)
    file_path = RUNS_DIR / run_name / f"{file_stem}.md"
    if not file_path.exists():
        return JSONResponse({"error": "File not found"}, status_code=404)
    return {"content": file_path.read_text()}


@app.post("/api/runs/{run_name}/action")
async def api_action(run_name: str, body: dict):
    if not re.match(r'^[\w\-]+$', run_name):
        return JSONResponse({"error": "Invalid run name"}, status_code=400)

    stage  = body.get("stage",  "").lower()
    action = body.get("action", "").lower()
    comment = body.get("comment", "").strip()

    if stage not in ("architecture", "planning", "implementation"):
        return JSONResponse({"error": "Invalid stage"}, status_code=400)
    if action not in ("approve", "request_changes", "hold"):
        return JSONResponse({"error": "Invalid action"}, status_code=400)

    board_path = RUNS_DIR / run_name / "approval-board.md"
    if not board_path.exists():
        return JSONResponse({"error": "approval-board.md not found"}, status_code=404)

    content   = board_path.read_text()
    stage_cap = stage.capitalize()
    ts        = datetime.now().strftime("%Y-%m-%d %H:%M")

    ACTION_MAP = {
        "approve":         ("✅ Approved",          "**Approved**"),
        "request_changes": ("🔄 Changes Requested", "**Changes Requested**"),
        "hold":            ("⏸ On Hold",            "**On Hold**"),
    }
    status_label, decision_label = ACTION_MAP[action]

    # Update the matching row in the Stage Status table
    lines = content.split('\n')
    new_lines = []
    for line in lines:
        if line.strip().startswith('|') and stage_cap in line:
            cols = line.split('|')
            if len(cols) >= 5:
                cols[2] = f' {status_label} '
                if len(cols) > 5:
                    cols[5] = f' {decision_label} '
                line = '|'.join(cols)
        new_lines.append(line)
    content = '\n'.join(new_lines)

    if action == "approve":
        content = content.replace(
            f'- [ ] {stage_cap} approved',
            f'- [x] {stage_cap} approved',
        )

    content = re.sub(
        r'- Last updated:.*',
        f'- Last updated: `{ts} — {stage_cap} {action.replace("_", " ")} via dashboard`',
        content,
    )

    if comment:
        content += f'\n\n> **Dashboard [{ts}]:** {stage_cap} — {action}: {comment}\n'

    board_path.write_text(content)
    return {"ok": True, "message": f"{stage_cap} marked as {action} at {ts}"}


@app.get("/api/status")
async def api_status():
    return {"connections": manager.count, "watching": str(RUNS_DIR)}


# ─── WebSocket ────────────────────────────────────────────────────────────────

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await manager.connect(ws)
    try:
        await ws.send_json({"type": "init", "runs_list": list_runs(RUNS_DIR)})
        while True:
            msg = await ws.receive_text()
            if msg == "ping":
                await ws.send_text("pong")
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(ws)


# ─── Static Files ─────────────────────────────────────────────────────────────

app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")


# ─── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8765, log_level="warning")
