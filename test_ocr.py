import os
from PIL import Image, ImageDraw, ImageFont

def create_dummy_image(path):
    img = Image.new('RGB', (800, 400), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    
    # Try using a default font, usually available on Windows
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except IOError:
        font = ImageFont.load_default()
    
    text = (
        "Customer Information:\n"
        "Name: John Doe\n"
        "Credit Card: 4111 1111 1111 1111\n"
        "Debit Card: 5500 0000 0000 0000\n"
        "Aadhaar No: 1234 5678 9012\n"
        "PAN No: ABCDE1234F\n"
    )
    
    d.text((20, 20), text, fill=(0, 0, 0), font=font)
    img.save(path)

if __name__ == "__main__":
    from dlp_agent.scanner.stream_processor import StreamProcessor
    from dlp_agent.events.sinks import EventSink

    class ConsoleSink(EventSink):
        def emit(self, event):
            print(f"FOUND: {event.rule} = {event.masked_value} (Hash: {event.hash})")

    # Create dummy image
    image_path = "dummy_sensitive_data.png"
    print(f"Creating test image at {image_path}...")
    create_dummy_image(image_path)

    config = {
        "rules": {
            "card": {"enabled": True},
            "aadhaar": {"enabled": True},
            "pan": {"enabled": True}
        }
    }

    sinks = [ConsoleSink()]
    processor = StreamProcessor(config, sinks)
    
    print("\nScanning image...")
    count = processor.process_file(image_path)
    
    print(f"\nTotal findings: {count}")
    
    # Cleanup
    if os.path.exists(image_path):
        os.remove(image_path)
