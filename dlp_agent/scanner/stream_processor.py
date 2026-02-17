import logging
from dlp_agent.detectors import detect_credit_cards, detect_aadhaar, detect_pan
from dlp_agent.events.sinks import EventSink

class StreamProcessor:
    def __init__(self, config: dict, sinks: list[EventSink] = None):
        self.config = config
        self.sinks = sinks or []
        self.detectors = []
        self.seen_hashes = set() # For deduplication
        self._init_detectors()

    def _init_detectors(self):
        rules = self.config.get('rules', {})
        if rules.get('card', {}).get('enabled', False):
            self.detectors.append(detect_credit_cards)
        if rules.get('aadhaar', {}).get('enabled', False):
            self.detectors.append(detect_aadhaar)
        if rules.get('pan', {}).get('enabled', False):
            self.detectors.append(detect_pan)

    def process_file(self, file_path: str) -> int:
        """
        Process a file and emit findings to sinks.
        Returns the count of findings.
        """
        findings_count = 0
        try:
            # Using 'errors="ignore"' to skip decoding errors
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    line_content = line.strip()
                    if not line_content:
                        continue
                        
                    for detector in self.detectors:
                        file_events = detector(line_content)
                        for event in file_events:
                            # Populate source info
                            event.source = {
                                "type": "file",
                                "path": file_path,
                                "line": line_num
                            }
                            
                            # Deduplication check
                            # Key: hash + rule + file + line
                            dedup_key = f"{event.hash}:{event.rule}:{file_path}:{line_num}"
                            
                            if dedup_key in self.seen_hashes:
                                continue
                                
                            self.seen_hashes.add(dedup_key)
                            
                            # Emit to all sinks
                            for sink in self.sinks:
                                sink.emit(event)
                                
                            findings_count += 1
                            
        except Exception as e:
            logging.error(f"Error processing file {file_path}: {str(e)}")
            
        return findings_count
