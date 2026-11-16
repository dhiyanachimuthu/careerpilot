from pathlib import Path
from uuid import uuid4
from io import BytesIO
import pymupdf
from docx import Document

MAX_BYTES = 5 * 1024 * 1024
EXTENSIONS = {'.pdf','.docx','.txt'}
UPLOADS = Path(__file__).resolve().parent / 'uploads'

def validate(filename, content):
    ext = Path(filename).suffix.lower()
    if ext not in EXTENSIONS:
        raise ValueError('Only PDF, DOCX and TXT resumes are supported.')
    if not content or len(content) > MAX_BYTES:
        raise ValueError('Resume must be nonempty and at most 5 MB.')
    return ext

def extract_text(filename, content):
    ext = validate(filename, content)
    if ext == '.pdf':
        with pymupdf.open(stream=content, filetype='pdf') as doc:
            text = '\n'.join(page.get_text() for page in doc)
    elif ext == '.docx':
        doc = Document(BytesIO(content))
        lines = [p.text for p in doc.paragraphs]
        for table in doc.tables:
            for row in table.rows:
                lines.append(' | '.join(cell.text for cell in row.cells))
        text = '\n'.join(lines)
    else:
        text = content.decode('utf-8-sig')
    if not text.strip():
        raise ValueError('No readable text found. Scanned PDFs require OCR.')
    return text.strip()

def store_file(filename, content):
    ext = validate(filename, content)
    UPLOADS.mkdir(parents=True, exist_ok=True)
    path = UPLOADS / (uuid4().hex + ext)
    path.write_bytes(content)
    return {'filename': Path(filename).name, 'file_type': ext,
            'file_size': len(content), 'stored_path': str(path.relative_to(UPLOADS.parent))}
