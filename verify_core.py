import sys
import os
import unittest

# Ensure we can import the module
sys.path.append(os.getcwd())

from dlp_agent.detectors.credit_card import detect_credit_cards
from dlp_agent.detectors.aadhaar import detect_aadhaar
from dlp_agent.detectors.pan import detect_pan
from dlp_agent.scanner.file_walker import FileWalker
from dlp_agent.scanner.stream_processor import StreamProcessor

class TestCore(unittest.TestCase):
    def test_credit_card(self):
        # 4000 0000 0000 0002 passes Luhn (4*2=8 + 2 = 10)
        text = "Card: 4000 0000 0000 0002"
        findings = detect_credit_cards(text)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]['type'], 'Credit Card')
        
    def test_pan(self):
        text = "PAN: ABCDE1234F"
        findings = detect_pan(text)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]['type'], 'PAN')

    def test_aadhaar(self):
        # 9999 9999 0019 is valid verhoeff
        text = "ADR: 9999 9999 0019" 
        findings = detect_aadhaar(text)
        self.assertEqual(len(findings), 1)

    def test_scanner_config(self):
        config = {
            "scan": {"allowedExtensions": [".py"], "excludedPaths": []},
            "rules": {}
        }
        walker = FileWalker(config)
        # Should find this script itself
        files = list(walker.walk('.'))
        self.assertTrue(any("verify_core.py" in f for f in files))

if __name__ == '__main__':
    unittest.main()
