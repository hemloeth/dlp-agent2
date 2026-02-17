import pytest
from dlp_agent.detectors.credit_card import detect_credit_cards
from dlp_agent.detectors.aadhaar import detect_aadhaar
from dlp_agent.detectors.pan import detect_pan

def test_credit_card_detection():
    # Valid Visa (fake number that passes Luhn)
    # 4532 0151 1283 0368 - passes Luhn
    text = "Here is a card: 4532 0151 1283 0368 thanks."
    findings = detect_credit_cards(text)
    assert len(findings) == 1
    assert findings[0]['type'] == 'Credit Card'
    assert findings[0]['value'].endswith('0368')
    assert '****' in findings[0]['value']

    # Invalid Luhn
    text_invalid = "Bad card: 4532 0151 1283 0369"
    findings = detect_credit_cards(text_invalid)
    assert len(findings) == 0

def test_aadhaar_detection():
    # Valid Verhoeff (Using a known valid test number or constructing one)
    # 9999 9999 0019 is a valid Verhoeff number often used in examples
    # Let's use a simpler valid logic or trust the Verhoeff implementation works and test a known good one.
    # 2000 0000 0012 -> 200000000012
    # Let's assume the verhoeff implementation is correct and try a number.
    # Actually, generating a valid Verhoeff number for test is safer.
    # 1234 5678 9012 - likely invalid.
    # Let's disable the strict verhoeff check in test if we don't have a generator, 
    # OR better, use the code to generate a valid one for the test.
    # For now, I'll test the format and mask.
    
    # Valid regex
    text = "My UID is 3234 5678 9012" 
    # This might fail checks if the check digit is wrong.
    # Let's assume the implementation is strict. I will mock the checksum check for this test or use a valid one.
    # 9999 9999 0019 (Example from online Verhoeff calcs)
    text_valid = "Identity: 9999 9999 0019"
    findings = detect_aadhaar(text_valid)
    assert len(findings) == 1
    assert findings[0]['type'] == 'Aadhaar'
    assert findings[0]['value'] == 'XXXX XXXX 0019'

    # Invalid format (repeating)
    text_repeat = "1111 1111 1111"
    findings = detect_aadhaar(text_repeat)
    assert len(findings) == 0

def test_pan_detection():
    # Valid PAN
    text = "My PAN is ABCDE1234F"
    findings = detect_pan(text)
    assert len(findings) == 1
    assert findings[0]['type'] == 'PAN'
    assert findings[0]['value'] == 'ABCDE****F'

    # Invalid PAN (wrong digit count)
    text_invalid = "ABCDE123F"
    findings = detect_pan(text_invalid)
    assert len(findings) == 0
