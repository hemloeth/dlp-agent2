import re
from dlp_agent.utils.checksums import luhn_check
from dlp_agent.events.model import DetectionEvent

# Regex for finding potential card numbers (13-19 digits, allowing spaces/hyphens)
CC_PATTERN = re.compile(r'\b(?:\d[ -]*?){13,19}\b')

def detect_credit_cards(text: str) -> list[DetectionEvent]:
    """
    Scan text for credit card numbers.
    Returns a list of DetectionEvent objects.
    """
    findings = []
    
    for match in CC_PATTERN.finditer(text):
        raw_match = match.group()
        # Clean the match (remove spaces, hyphens)
        clean_number = re.sub(r'[ -]', '', raw_match)
        
        # Length check - User specifically requested "any 16 digit" to be founds
        # Original spec was 13-19, but user request overrides for broad 16-digit detection.
        # We will keep the 13-19 regex to capture them, but VALIDATE any 16 digit number blindly.
        if len(clean_number) == 16:
            event = DetectionEvent.create(
                rule="Credit Card",
                severity="Medium", # Lower confidence since no checksum
                raw_value=clean_number,
                masked_value=mask_credit_card(clean_number),
                source={}, # To be populated by scanner
                context_snippet=None
            )
            findings.append(event)
            continue

        # For non-16 digit numbers (13-15, 17-19)
        if 13 <= len(clean_number) <= 19:
             if luhn_check(clean_number):
                event = DetectionEvent.create(
                    rule="Credit Card",
                    severity="High",
                    raw_value=clean_number,
                    masked_value=mask_credit_card(clean_number),
                    source={},
                    context_snippet=None
                )
                findings.append(event)
            
    return findings

def mask_credit_card(number: str) -> str:
    """Masks credit card number: ************1111"""
    if len(number) < 4:
        return number 
    return '*' * (len(number) - 4) + number[-4:]
