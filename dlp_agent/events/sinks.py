from abc import ABC, abstractmethod
import click
import json
import logging
from dataclasses import asdict
from dlp_agent.events.model import DetectionEvent

class EventSink(ABC):
    @abstractmethod
    def emit(self, event: DetectionEvent):
        pass

    def flush(self):
        pass

class CliSink(EventSink):
    """Prints human-readable messages to stdout (using click)."""
    def emit(self, event: DetectionEvent):
        source_str = f"{event.source.get('path', 'unknown')}"
        if 'line' in event.source:
             source_str += f":{event.source['line']}"
        
        msg = f"I have found the {event.rule} details: {event.masked_value} in {event.source.get('path')} at line {event.source.get('line')}"
        click.echo(msg)

class JsonSink(EventSink):
    """Writes JSON lines to a file (or stdout if file is None)."""
    def __init__(self, file_path: str = None):
        self.file_path = file_path
        self.file_handle = None
        if self.file_path:
            self.file_handle = open(self.file_path, 'a', encoding='utf-8')

    def emit(self, event: DetectionEvent):
        json_str = event.to_json()
        if self.file_handle:
            self.file_handle.write(json_str + '\n')
        else:
            click.echo(json_str)

    def flush(self):
        if self.file_handle:
            self.file_handle.flush()
            
    def close(self):
        if self.file_handle:
            self.file_handle.close()

class WebSink(EventSink):
    """POSTs each detection event as JSON to a remote dashboard endpoint."""

    def __init__(self, url: str = "https://dlp.gtis.ai/dashboard/logs"):
        try:
            import requests as _requests
            self._requests = _requests
        except ImportError:
            raise ImportError(
                "The 'requests' library is required for WebSink. "
                "Install it with: pip install requests"
            )
        self.url = url
        self._session = self._requests.Session()
        self._session.headers.update({"Content-Type": "application/json"})

    def emit(self, event: DetectionEvent):
        payload = asdict(event)
        try:
            response = self._session.post(self.url, json=payload, timeout=5)
            if not response.ok:
                logging.warning(
                    f"[WebSink] Dashboard returned {response.status_code} for event {event.event_id}"
                )
        except Exception as exc:
            logging.warning(f"[WebSink] Failed to send event to dashboard: {exc}")

    def flush(self):
        pass

