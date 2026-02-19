import uuid
import hashlib
import json
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Optional

@dataclass
class DetectionEvent:
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    agent_id: str = "node-001"  # Default agent ID, could be configured
    rule: str = "UNKNOWN"
    severity: str = "medium"
    masked_value: str = ""
    hash: str = ""
    source: dict = field(default_factory=dict)
    context: Optional[dict] = None

    @staticmethod
    def create(rule: str, severity: str, raw_value: str, masked_value: str, source: dict, context_snippet: str = None) -> 'DetectionEvent':
        raw_hash = hashlib.sha256(raw_value.encode('utf-8')).hexdigest()
        
        context = None
        if context_snippet:
             context = {"snippet": context_snippet[:120]} # Max 120 chars constraint

        return DetectionEvent(
            rule=rule,
            severity=severity,
            masked_value=masked_value,
            hash=raw_hash,
            source=source,
            context=context
        )

    def to_json(self) -> str:
        return json.dumps(asdict(self))
