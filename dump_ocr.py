import easyocr
import sys
import io

# Force stdout to utf-8 properly to avoid PowerShell piping issues
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

reader = easyocr.Reader(['en'])
img_path = r'c:\Users\DELL 5310\Desktop\cr.png'
text = reader.readtext(img_path, detail=0)

with open('debug_ocr.txt', 'w', encoding='utf-8') as f:
    for line in text:
        f.write(line + '\n')
