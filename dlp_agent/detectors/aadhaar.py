import re
from dlp_agent.utils.checksums import verhoeff_check
from dlp_agent.events.model import DetectionEvent

# Aadhaar: 12 digits, optional spaces used as separators.
# Configurable to prevent picking up standard large numbers if needed.
# Pattern ensures it starts with 2-9 if spaces are used or not.
AADHAAR_PATTERN = re.compile(r'\b[2-9]\d{3}\s?\d{4}\s?\d{4}\b')

def detect_aadhaar(text: str) -> list[DetectionEvent]:
    """
    Scan text for Aadhaar numbers.
    Returns a list of DetectionEvent objects.
    """
    findings = []
    
    for match in AADHAAR_PATTERN.finditer(text):
        raw_match = match.group()
        clean_number = raw_match.replace(' ', '')
        
        if len(clean_number) != 12:
            continue

        # Exclusion: Repeated digits (e.g., 1111 1111 1111) are often test data or not valid
        if len(set(clean_number)) == 1:
            continue
            
        if verhoeff_check(clean_number):
            event = DetectionEvent.create(
                rule="Aadhaar",
                severity="Critical",
                raw_value=clean_number,
                masked_value=mask_aadhaar(clean_number),
                source={},
                context_snippet=None
            )
            findings.append(event)
            
    return findings

def mask_aadhaar(number: str) -> str:
    """Masks Aadhaar number: XXXX XXXX 9012"""
    # Standard format often includes spaces for readability
    return "XXXX XXXX " + number[-4:]
