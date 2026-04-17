#parses the pdf docs and plain text into and preserves section structure for citation in risk report 

import pdfplumber
import re
from pathlib import Path

def parse_document(file_path: str) -> dict:
    path = Path(file_path)
    
    if path.suffix.lower() == ".pdf":
        return _parse_pdf(file_path)
    return {"text": path.read_text(encoding="utf-8"), "pages": [], "source": path.name}

def _parse_pdf(file_path: str) -> dict:
    pages = []
    full_text = []
    
    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            pages.append({"page": i + 1, "text": text})
            full_text.append(text)
    
    return {
        "text": "\n".join(full_text),
        "pages": pages,
        "source": Path(file_path).name
    }

def detect_sections(text: str) -> list:
    """
    Detects Item headers (SEC filings) and Article/Section headers
    (regulations) and returns a list of (title, start_index) tuples.
    """
    patterns = [
        r"(Item\s+\d+[A-Z]?\.\s+[A-Z][^\n]{5,60})",   # SEC 10-K items
        r"(Article\s+\d+[\.\s][^\n]{5,60})",             # EU regulations - optional
        r"(§\s*\d+[\.\d]+\s+[^\n]{5,60})",              # US code sections - 
        r"(Section\s+\d+[\.\d]*\s+[^\n]{5,60})",        # Generic sections
    ]
    combined = "|".join(patterns)
    matches = [(m.group(), m.start()) for m in re.finditer(combined, text)]
    return matches