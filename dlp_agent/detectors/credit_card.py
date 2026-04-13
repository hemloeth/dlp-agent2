import re
import urllib.request
import urllib.error
from dlp_agent.utils.checksums import luhn_check
from dlp_agent.events.model import DetectionEvent

# Regex for finding potential card numbers (13-19 digits, allowing spaces/hyphens)
CC_PATTERN = re.compile(r'\b(?:\d[ -]*?){13,19}\b')

def check_bin_exists(bin_number: str) -> bool:
    """Checks if a 6-digit BIN exists via the specified API."""
    url = f"https://binapi-chty.onrender.com/api/bins/{bin_number}"
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.status == 200
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False
        return None
    except Exception:
        return None

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
        
        # Check BIN first (first 6 digits)
        if len(clean_number) >= 6:
            bin_number = clean_number[:6]
            if check_bin_exists(bin_number) is False:
                continue
                
        # Standard logic for all supported lengths (13-19 digits)
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
