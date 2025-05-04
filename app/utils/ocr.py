import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import os
import logging

# Set the path to Tesseract executable (update if needed)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    return "\n".join([page.get_text() for page in doc])

def extract_text_from_image(image_path):
    img = Image.open(image_path)
    return pytesseract.image_to_string(img)

def extract_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext in [".pdf"]:
        text = extract_text_from_pdf(file_path)
    elif ext in [".png", ".jpg", ".jpeg"]:
        text = extract_text_from_image(file_path)
    else:
        raise ValueError("Unsupported file format.")
    
    logging.info(f"Extracted text from {file_path}: {text[:500]}")
    return text

