import json
import os

DEFAULT_POLICY = {
    "rules": {
        "aadhaar": { "enabled": True, "severity": "CRITICAL" },
        "pan": { "enabled": True, "severity": "HIGH" },
        "card": { "enabled": True, "severity": "HIGH" }
    },
    "scan": {
        "maxFileSizeMB": 10,
        "allowedExtensions": [".txt", ".log", ".csv", ".json", ".xml", ".md"],
        "excludedPaths": ["/proc", "/sys", "/dev", "/node_modules", "/.git"]
    }
}

def load_policy(policy_path: str) -> dict:
    """Load policy from JSON file or return default if not found."""
    if os.path.exists(policy_path):
        with open(policy_path, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: Invalid JSON in {policy_path}, using default policy.")
    return DEFAULT_POLICY
