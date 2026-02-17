import re
from dlp_agent.events.model import DetectionEvent

# PAN: 5 letters, 4 digits, 1 letter. Case insensitive usually, but official PAN is uppercase.
# We will match case-insensitively as per requirements.
PAN_PATTERN = re.compile(r'\b[A-Za-z]{5}[0-9]{4}[A-Za-z]{1}\b')

def detect_pan(text: str) -> list[DetectionEvent]:
    """
    Scan text for PAN numbers.
    Returns a list of DetectionEvent objects.
    """
    findings = []
    
    for match in PAN_PATTERN.finditer(text):
        raw_match = match.group()
        # No checksum available for PAN publicly (it exists but is proprietary/complex).
        # Regex is strong enough for this context as per spec.
        
        event = DetectionEvent.create(
            rule="PAN",
            severity="High",
            raw_value=raw_match,  # PAN is often alphanumeric, so keep case? Raw match has dashes? 
                                  # Regex doesn't match dashes here. 
                                  # Let's keep raw match as is.
            masked_value=mask_pan(raw_match),
            source={},
            context_snippet=None
        )
        findings.append(event)
            
    return findings

def mask_pan(number: str) -> str:
    """Masks PAN number: ABCDE****F"""
    # Keep first 5 chars, mask 4 digits, keep last char
    return number[:5] + '****' + number[-1]
