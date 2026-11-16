from io import BytesIO
import json
import pymupdf
from docx import Document
import database
from resume_parser import extract_text, validate
from llm_extractor import CandidateExtraction

def test_txt():
    assert 'Python' in extract_text('a.txt', b'Skills: Python')

def test_reject_invalid():
    try:
        validate('bad.exe', b'hello')
    except ValueError:
        pass
    else:
        raise AssertionError('Executable file should be rejected')

def test_pdf():
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((72,72),'Skills: SQL')
    data = doc.tobytes()
    doc.close()
    assert 'SQL' in extract_text('test.pdf',data)

def test_docx():
    doc = Document()
    doc.add_paragraph('Skills: React')
    buffer = BytesIO()
    doc.save(buffer)
    assert 'React' in extract_text('test.docx',buffer.getvalue())

def test_schema():
    p = CandidateExtraction.model_validate({'skills':['Python'], 'education':[]})
    assert p.skills == ['Python'] and p.projects == []

def test_database(tmp_path, monkeypatch):
    monkeypatch.setattr(database,'DB',tmp_path/'test.db')
    database.create_tables()
    cid = database.create_candidate('Test Student','test@example.com')
    database.add_resume(cid,{'filename':'resume.txt','file_type':'.txt',
                            'file_size':3,'stored_path':'uploads/test.txt'})
    database.save_extraction(cid, CandidateExtraction(skills=['SQL']).model_dump())
    assert json.loads(database.candidate(cid)['skills']) == ['SQL']
    assert database.resumes(cid)[0]['filename'] == 'resume.txt'
