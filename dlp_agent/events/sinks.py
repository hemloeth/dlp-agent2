from abc import ABC, abstractmethod
import click
import json
from typing import List
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
        
        # Format similar to Phase 0 requests but using Event data
        # "I have found the [Type] details: [Value] in [File] at line [Line]"
        # Mapping Rule -> Type for display if needed, or just use rule
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
