import re
import urllib.request
import urllib.error
from dlp_agent.utils.checksums import luhn_check
from dlp_agent.events.model import DetectionEvent

# Tighter pattern: digits optionally separated by spaces or hyphens, word-bounded
CC_PATTERN = re.compile(r'\b(\d{4}[ -]?\d{4}[ -]?\d{4}[ -]?\d{1,7}|\d{13,19})\b')

POSITIVE_KEYWORDS = [
    'card', 'credit', 'debit', 'visa', 'mastercard', 'amex', 'discover',
    'payment', 'cvv', 'cvc', 'expir', 'billing', 'checkout', 'pan',
    'cardholder', 'transaction', 'charge', 'merchant', 'bank'
]

NEGATIVE_KEYWORDS = [
    'phone', 'tel', 'mobile', 'invoice', 'order', 'tracking', 'employee',
    'model', 'serial', 'version', 'build', 'zip', 'postal', 'id:', 'ref'
]


def check_bin_exists(bin_number: str) -> bool | None:
    """
    Returns:
        True  — BIN confirmed valid
        False — BIN confirmed invalid (404)
        None  — API unreachable / timeout (treat as inconclusive)
    """
    url = f"https://binapi-chty.onrender.com/api/bins/{bin_number}"
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.status == 200
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False
        return None  # 5xx or other HTTP errors — inconclusive
    except Exception:
        return None  # network timeout, DNS failure, etc.


def context_score(text: str, match_start: int, window: int = 120) -> int:
    """Score the context around a match. Positive = more likely a real card."""
    snippet = text[max(0, match_start - window): match_start + window].lower()
    score = sum(2 for kw in POSITIVE_KEYWORDS if kw in snippet)
    score -= sum(3 for kw in NEGATIVE_KEYWORDS if kw in snippet)
    return score


def detect_credit_cards(
    text: str,
    require_bin: bool = True,
    context_threshold: int = 0,  # 0 = neutral, raise to 2+ for stricter
) -> list[DetectionEvent]:
    """
    Scan text for credit card numbers.
    Returns a list of DetectionEvent objects.
    """
    findings = []

    for match in CC_PATTERN.finditer(text):
        raw_match = match.group()
        clean_number = re.sub(r'[ -]', '', raw_match)

        # Length guard (also catches regex edge cases)
        if not (13 <= len(clean_number) <= 19):
            continue

        # BIN check (first 6 digits)
        if require_bin and len(clean_number) >= 6:
            bin_result = check_bin_exists(clean_number[:6])
            if bin_result is False:
                # Confirmed invalid BIN — skip
                continue
            # bin_result is True or None: proceed to Luhn either way

        # Luhn check — always runs, not nested under BIN block
        if not luhn_check(clean_number):
            continue

        # Context scoring — skip likely false positives
        if context_score(text, match.start()) < context_threshold:
            continue

        event = DetectionEvent.create(
            rule="Credit Card",
            severity="High",
            raw_value=clean_number,
            masked_value=mask_credit_card(clean_number),
            source={},
            context_snippet=_extract_snippet(text, match.start()),
        )
        findings.append(event)

    return findings


def mask_credit_card(number: str) -> str:
    """Masks all but last 4 digits: ************1111"""
    if len(number) < 4:
        return number
    return '*' * (len(number) - 4) + number[-4:]


def _extract_snippet(text: str, pos: int, window: int = 60) -> str:
    """Returns surrounding text for the context_snippet field."""
    start = max(0, pos - window)
    end = min(len(text), pos + window)
    return text[start:end].strip()
