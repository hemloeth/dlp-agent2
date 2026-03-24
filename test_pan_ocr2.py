import sys
import os
import glob
sys.path.append(os.getcwd())
try:
    from dlp_agent.utils.ocr_extractor import OCRExtractor
    from dlp_agent.detectors.pan import detect_pan
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

extractor = OCRExtractor()
img_dir = r"C:\Users\DELL 5310\Desktop\Refrence dlp agent"
imgs = glob.glob(os.path.join(img_dir, "*.jpeg")) + glob.glob(os.path.join(img_dir, "*.jpg")) + glob.glob(os.path.join(img_dir, "*.png"))

with open("ocr_output.txt", "w", encoding="utf-8") as f:
    for img in imgs:
        f.write(f"\n--- Testing {img} ---\n")
        lines = extractor.extract_text_from_image(img)
        f.write("Extracted Lines:\n")
        for line in lines:
            f.write(f"{repr(line)}\n")
        f.write("\nPAN Detection Results:\n")
        for line in lines:
            findings = detect_pan(line)
            if findings:
                for fd in findings:
                    f.write(f"FOUND: {fd.raw_value}\n")
print("Done writing to ocr_output.txt")
