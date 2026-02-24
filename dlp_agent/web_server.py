import json
import os
import threading
import time
import webbrowser
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Optional
from urllib.parse import parse_qs, urlparse

from dlp_agent.config import load_policy
from dlp_agent.events.sinks import EventSink, JsonSink
from dlp_agent.scanner import FileWalker, StreamProcessor


class _MemorySink(EventSink):
    def __init__(self, server: "WebScanServer"):
        self._server = server

    def emit(self, event):
        self._server._add_event(event)


class WebScanServer:
    def __init__(
        self,
        *,
        host: str = "127.0.0.1",
        port: int = 8765,
        default_policy_path: str = "config/policy.json",
        debug: bool = False,
        json_out: Optional[str] = None,
        open_browser: bool = True,
    ):
        self.host = host
        self.port = int(port)
        self.default_policy_path = default_policy_path
        self.debug = debug
        self.json_out = json_out
        self.open_browser = open_browser

        self._lock = threading.Lock()
        self._scan_thread: Optional[threading.Thread] = None
        self._next_event_id = 1
        self._events: list[dict[str, Any]] = []
        self._state: dict[str, Any] = {
            "status": "idle",  # idle|running|done|error
            "scan_dir": None,
            "policy": self.default_policy_path,
            "started_at": None,
            "finished_at": None,
            "current_file": None,
            "scanned_files": 0,
            "total_findings": 0,
            "error": None,
        }

    def serve_forever(self):
        handler_cls = self._make_handler()
        httpd = ThreadingHTTPServer((self.host, self.port), handler_cls)
        httpd.web_scan_server = self  # type: ignore[attr-defined]

        url = f"http://{self.host}:{self.port}/"
        if self.open_browser:
            try:
                webbrowser.open(url)
            except Exception:
                pass

        httpd.serve_forever()

    def start_scan(self, scan_dir: str, policy_path: Optional[str] = None) -> bool:
        scan_dir = os.path.abspath(scan_dir)
        policy_path = policy_path or self.default_policy_path

        with self._lock:
            if self._state["status"] == "running":
                return False

            self._events.clear()
            self._next_event_id = 1
            self._state.update(
                {
                    "status": "running",
                    "scan_dir": scan_dir,
                    "policy": policy_path,
                    "started_at": time.time(),
                    "finished_at": None,
                    "current_file": None,
                    "scanned_files": 0,
                    "total_findings": 0,
                    "error": None,
                }
            )

            t = threading.Thread(
                target=self._run_scan,
                args=(scan_dir, policy_path),
                name="dlp-web-scan",
                daemon=True,
            )
            self._scan_thread = t
            t.start()
            return True

    def _run_scan(self, scan_dir: str, policy_path: str):
        try:
            policy_config = load_policy(policy_path)
            sinks: list[EventSink] = [_MemorySink(self)]
            if self.json_out:
                sinks.append(JsonSink(self.json_out))

            walker = FileWalker(policy_config, debug=self.debug)
            processor = StreamProcessor(policy_config, sinks=sinks)

            total_findings = 0
            scanned_files = 0

            for file_path in walker.walk(os.path.abspath(scan_dir)):
                with self._lock:
                    self._state["current_file"] = file_path
                    self._state["scanned_files"] = scanned_files
                    self._state["total_findings"] = total_findings

                scanned_files += 1
                total_findings += processor.process_file(file_path)

            with self._lock:
                self._state["current_file"] = None
                self._state["scanned_files"] = scanned_files
                self._state["total_findings"] = total_findings
                self._state["status"] = "done"
                self._state["finished_at"] = time.time()
        except Exception as e:
            with self._lock:
                self._state["status"] = "error"
                self._state["error"] = str(e)
                self._state["finished_at"] = time.time()

    def _add_event(self, event):
        data = asdict(event)
        with self._lock:
            data["id"] = self._next_event_id
            self._next_event_id += 1
            self._events.append(data)
            # Cap memory in case of huge scans
            if len(self._events) > 5000:
                self._events = self._events[-5000:]

    def _snapshot(self) -> dict[str, Any]:
        with self._lock:
            return {
                "state": dict(self._state),
                "last_event_id": (self._next_event_id - 1),
            }

    def _events_since(self, since_id: int) -> dict[str, Any]:
        with self._lock:
            # events are ordered; slice by scanning from end until we find <= since_id
            if since_id <= 0:
                evs = list(self._events)
            else:
                # small list; linear scan is fine
                evs = [e for e in self._events if int(e.get("id", 0)) > since_id]

            return {"events": evs, "last_event_id": (self._next_event_id - 1)}

    def _make_handler(self):
        server = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, fmt, *args):
                # Keep server quiet unless debugging is needed.
                if server.debug:
                    super().log_message(fmt, *args)

            def _send_json(self, obj: Any, status: int = 200):
                body = json.dumps(obj).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def _send_html(self, html: str, status: int = 200):
                body = html.encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_GET(self):
                parsed = urlparse(self.path)
                if parsed.path == "/":
                    self._send_html(_INDEX_HTML)
                    return
                if parsed.path == "/api/status":
                    self._send_json(server._snapshot())
                    return
                if parsed.path == "/api/events":
                    qs = parse_qs(parsed.query or "")
                    try:
                        since = int((qs.get("since") or ["0"])[0])
                    except Exception:
                        since = 0
                    self._send_json(server._events_since(since))
                    return
                self._send_json({"error": "not_found"}, status=404)

            def do_POST(self):
                parsed = urlparse(self.path)
                if parsed.path != "/api/start":
                    self._send_json({"error": "not_found"}, status=404)
                    return

                try:
                    length = int(self.headers.get("Content-Length") or "0")
                except Exception:
                    length = 0
                raw = self.rfile.read(length) if length > 0 else b"{}"

                try:
                    payload = json.loads(raw.decode("utf-8"))
                except Exception:
                    self._send_json({"error": "invalid_json"}, status=400)
                    return

                scan_dir = (payload.get("scan_dir") or "").strip()
                policy = (payload.get("policy") or "").strip() or None
                if not scan_dir:
                    self._send_json({"error": "scan_dir_required"}, status=400)
                    return

                started = server.start_scan(scan_dir, policy_path=policy)
                if not started:
                    self._send_json({"ok": False, "reason": "already_running"}, status=409)
                    return

                self._send_json({"ok": True})

        return Handler


_INDEX_HTML = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>DLP Scanner</title>
    <style>
      :root { color-scheme: light dark; }
      body { font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; margin: 18px; }
      .row { display: flex; gap: 12px; flex-wrap: wrap; align-items: end; }
      label { display: block; font-size: 12px; opacity: 0.85; }
      input { min-width: 320px; padding: 8px 10px; border-radius: 8px; border: 1px solid rgba(127,127,127,0.35); }
      button { padding: 9px 12px; border-radius: 10px; border: 1px solid rgba(127,127,127,0.35); cursor: pointer; }
      pre { white-space: pre-wrap; word-break: break-word; padding: 12px; border-radius: 12px; border: 1px solid rgba(127,127,127,0.25); }
      .muted { opacity: 0.8; font-size: 12px; }
      .status { font-weight: 600; }
    </style>
  </head>
  <body>
    <h2>DLP Scanner</h2>
    <div class="row">
      <div>
        <label>Scan directory</label>
        <input id="scanDir" placeholder="C:\\Users\\YourName\\Desktop" />
      </div>
      <div>
        <label>Policy path (optional)</label>
        <input id="policy" placeholder="config/policy.json" />
      </div>
      <button id="startBtn">Start scan</button>
    </div>

    <p class="muted">
      This runs locally and uses your default browser (no embedded webview).
    </p>

    <p>
      Status: <span class="status" id="status">...</span><br/>
      Scanned files: <span id="scannedFiles">0</span> &nbsp;|&nbsp;
      Findings: <span id="totalFindings">0</span><br/>
      Current file: <span id="currentFile">-</span>
    </p>

    <h3>Findings</h3>
    <pre id="events">(waiting...)</pre>

    <script>
      let lastId = 0;
      const eventsEl = document.getElementById('events');
      const statusEl = document.getElementById('status');
      const scannedFilesEl = document.getElementById('scannedFiles');
      const totalFindingsEl = document.getElementById('totalFindings');
      const currentFileEl = document.getElementById('currentFile');

      function fmtEvent(e) {
        const src = e.source && e.source.path ? e.source.path : 'unknown';
        const line = e.source && e.source.line ? e.source.line : '?';
        return `[${e.severity}] ${e.rule}: ${e.masked_value}  (${src}:${line})`;
      }

      async function poll() {
        try {
          const st = await fetch('/api/status').then(r => r.json());
          const s = st.state || {};
          statusEl.textContent = s.status || 'unknown';
          scannedFilesEl.textContent = s.scanned_files ?? 0;
          totalFindingsEl.textContent = s.total_findings ?? 0;
          currentFileEl.textContent = s.current_file || '-';

          const ev = await fetch('/api/events?since=' + encodeURIComponent(lastId)).then(r => r.json());
          lastId = ev.last_event_id || lastId;
          const items = (ev.events || []).map(fmtEvent);
          if (items.length) {
            if (eventsEl.textContent === '(waiting...)') eventsEl.textContent = '';
            eventsEl.textContent += (eventsEl.textContent ? '\\n' : '') + items.join('\\n');
          }
        } catch (e) {
          statusEl.textContent = 'disconnected';
        } finally {
          setTimeout(poll, 700);
        }
      }

      document.getElementById('startBtn').addEventListener('click', async () => {
        const scan_dir = document.getElementById('scanDir').value.trim();
        const policy = document.getElementById('policy').value.trim();
        eventsEl.textContent = '';
        lastId = 0;
        const res = await fetch('/api/start', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ scan_dir, policy })
        });
        if (!res.ok) {
          const err = await res.json().catch(() => ({}));
          eventsEl.textContent = 'Could not start scan: ' + (err.error || res.status);
        }
      });

      poll();
    </script>
  </body>
</html>
"""

