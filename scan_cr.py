from dlp_agent.scanner.stream_processor import StreamProcessor
from dlp_agent.events.sinks import EventSink
from dlp_agent.utils.ocr_extractor import OCRExtractor
import os

class ConsoleSink(EventSink):
    def emit(self, event):
        print(f"FOUND: rule={event.rule}, masked_value={event.masked_value}, severity={event.severity}")

config = {
    "rules": {
        "card": {"enabled": True},
        "aadhaar": {"enabled": True},
        "pan": {"enabled": True}
    }
}

processor = StreamProcessor(config, [ConsoleSink()])
image_path = r"c:\Users\DELL 5310\Desktop\cr.png"

# We can also print all raw text extracted to show the user what it saw, since they asked "finf that the text from that"
print(f"Scanning image {image_path}...")
if os.path.exists(image_path):
    # Extract text manually first to print to user
    extractor = OCRExtractor()
    lines = extractor.extract_text_from_image(image_path)
    print("\n--- EXTRACTED TEXT ---")
    for line in lines:
        print(line)
    print("----------------------\n")
    
    # Process for sensitive data
    count = processor.process_file(image_path)
    print(f"\nTotal sensitive findings: {count}")
else:
    print(f"Image not found at {image_path}")
