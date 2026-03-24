import sys
import os
sys.path.append(os.getcwd())
try:
    from dlp_agent.utils.ocr_extractor import OCRExtractor
    from dlp_agent.detectors.pan import detect_pan
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

extractor = OCRExtractor()
img1 = r"C:\Users\DELL 5310\Desktop\Refrence dlp agent\WhatsApp Image 2026-03-20 at 3.16.30 PM.jpeg"
img2 = r"C:\Users\DELL 5310\Desktop\Refrence dlp agent\WhatsApp Image 2026-03-20 at 3.16.30 PMw.jpeg"

for img in [img1, img2]:
    print(f"\n--- Testing {img} ---")
    if os.path.exists(img):
        lines = extractor.extract_text_from_image(img)
        print("Extracted Lines:")
        for rule_line in lines:
            print(repr(rule_line))
            
        print("\nPAN Detection Results:")
        for line in lines:
            findings = detect_pan(line)
            if findings:
                for f in findings:
                    print(f"FOUND: {f.raw_value}")
    else:
        print(f"File not found: {img}")
