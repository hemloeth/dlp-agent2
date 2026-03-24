import logging
import os

try:
    import easyocr
except ImportError:
    easyocr = None

class OCRExtractor:
    def __init__(self, languages=['en']):
        if easyocr is None:
            logging.warning("EasyOCR is not installed. Image scanning will be disabled.")
            self.reader = None
        else:
            logging.info("Initializing EasyOCR. This might take a moment if models need to be downloaded.")
            gpu = False
            try:
                import torch
                torch.set_num_threads(1) # Disable PyTorch multi-threading
                gpu = torch.cuda.is_available()
            except ImportError:
                pass
            self.reader = easyocr.Reader(languages, gpu=gpu)

    def extract_text_from_image(self, image_path: str) -> list[str]:
        """
        Extracts text from an image.
        Returns a list of strings, where each string is a detected line of text.
        """
        if self.reader is None:
            logging.warning("Cannot extract text from image: EasyOCR is not initialized.")
            return []
            
        if not os.path.exists(image_path):
            logging.error(f"Image not found at path: {image_path}")
            return []

        try:
            # detail=0 returns a simple list of text strings instead of bounding boxes
            # workers=0 disables multiprocessing in easyocr
            result = self.reader.readtext(image_path, detail=0, workers=0)
            return result
        except Exception as e:
            logging.error(f"Error during OCR extraction for {image_path}: {e}")
            return []
