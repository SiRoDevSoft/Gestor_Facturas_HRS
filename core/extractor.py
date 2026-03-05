#extractor.py
import pdfplumber
import re
from utils.helpers import clean_currency

class PDFExtractor:
    def __init__(self):
        self.re_telefono = re.compile(r'\b\d{10}\b')
        self.re_monto = re.compile(r'[-+]?\s?\d+(?:\.\d{3})*(?:,\d{2})')

    def fetch_raw_data(self, pdf_file):
        """Extrae texto y lo organiza en una estructura cruda."""
        raw_rows = []
        full_text = ""
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                full_text += page.extract_text() + "\n"
        
        lines = full_text.split('\n')
        return lines, full_text