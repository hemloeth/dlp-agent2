import os
import pytest
from dlp_agent.scanner.file_walker import FileWalker
from dlp_agent.scanner.stream_processor import StreamProcessor

# Mock config
TEST_CONFIG = {
    "scan": {
        "maxFileSizeMB": 1,
        "allowedExtensions": [".txt"],
        "excludedPaths": ["/exclude_me"]
    },
    "rules": {
        "card": { "enabled": True },
        "aadhaar": { "enabled": True },
        "pan": { "enabled": True }
    }
}

def test_file_walker_exclusions(tmp_path):
    # Setup directories
    valid_dir = tmp_path / "valid"
    valid_dir.mkdir()
    excluded_dir = tmp_path / "exclude_me"
    excluded_dir.mkdir()
    
    # Create files
    (valid_dir / "test.txt").write_text("content")
    (valid_dir / "test.exe").write_text("binary") # Invalid extension
    (excluded_dir / "secret.txt").write_text("content")
    
    walker = FileWalker(TEST_CONFIG)
    
    files = list(walker.walk(str(tmp_path)))
    
    assert len(files) == 1
    # Check paths - normalize to avoid slash issues in test
    found_file = files[0].replace('\\', '/')
    assert found_file.endswith("valid/test.txt")

def test_stream_processor_detection(tmp_path):
    test_file = tmp_path / "sensitive.txt"
    test_file.write_text("My card is 4532 0151 1283 0368 and PAN is ABCDE1234F")
    
    processor = StreamProcessor(TEST_CONFIG)
    findings = processor.process_file(str(test_file))
    
    assert len(findings) == 2
    types = [f['type'] for f in findings]
    assert "Credit Card" in types
    assert "PAN" in types
    assert findings[0]['file'] == str(test_file)
