from typing import Dict, Any
import cv2
import pytesseract


def ocr_read(args: Dict[str, Any]) -> str:
    path = args.get("path")
    lang = args.get("lang", "tur+eng")
    img = cv2.imread(path)
    if img is None:
        return ""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray, lang=lang)
    return text
