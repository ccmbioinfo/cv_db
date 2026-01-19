#this is where all the helper functions go
import os

from docx import Document
import pymupdf
import pytesseract
from PIL import Image

SECTION_PATTERNS = [
    r"\s*EDUCATION",
    r"\s*EMPLOYMENT",
    r"\s*HONOURS AND CAREER AWARDS",
    r"\s*PROFESSIONAL AFFILIATIONS AND ACTIVITIES",
    r"\s*Research Funding",
    r"\s*Publications",
    r"\s*Intellectual Property",
    r"\s*Presentations and Special Lectures",
    r"\s*Teaching and Design",
    r"\s*Research Supervision",
    r"\s*Creative Professional Activities",
]

def check_file(path):
    if not(os.path.exists(path)):
        raise FileNotFoundError(path)

def extract_docx_text(docx_file):
    check_file(docx_file)
    doc = Document(docx_file)
    text=[]
    for para in doc.paragraphs:
        if para=="":
            continue
        else:
            text.append(para.text)
    return text

def extract_pdf_text(pdf_file, zoom=2):
    check_file(pdf_file)
    doc = pymupdf.open(pdf_file)
    zoom_x = zoom  # horizontal zoom
    zoom_y = zoom  # vertical zoom/
    mat = pymupdf.Matrix(zoom_x, zoom_y)
    texts = []
    for page in doc:
        pix=page.get_pixmap(matrix=mat)
        pix=Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        page_text=pytesseract.image_to_string(pix)
        texts.append(page_text)
    return texts




