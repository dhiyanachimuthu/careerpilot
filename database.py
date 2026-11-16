import json
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parent / "data" / "careerpilot.db"

def connect():
    DB.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys=ON")
    return connection

def create_tables():
    with connect() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS candidates (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          full_name TEXT NOT NULL, email TEXT NOT NULL UNIQUE,
          phone TEXT DEFAULT '', location TEXT DEFAULT '', summary TEXT DEFAULT '',
          skills TEXT DEFAULT '[]', education TEXT DEFAULT '[]',
          experience TEXT DEFAULT '[]', projects TEXT DEFAULT '[]',
          certifications TEXT DEFAULT '[]', created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
        c.execute("""CREATE TABLE IF NOT EXISTS resumes (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          candidate_id INTEGER NOT NULL REFERENCES candidates(id),
          filename TEXT NOT NULL, file_type TEXT NOT NULL,
          file_size INTEGER NOT NULL, stored_path TEXT NOT NULL,
          uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP)""")

def create_candidate(name, email, phone='', location=''):
    with connect() as c:
        cur = c.execute("INSERT INTO candidates (full_name,email,phone,location) VALUES (?,?,?,?)",
                        (name.strip(), email.strip(), phone.strip(), location.strip()))
        return cur.lastrowid

def candidates():
    with connect() as c:
        return [dict(r) for r in c.execute('SELECT * FROM candidates ORDER BY id DESC')]

def candidate(candidate_id):
    with connect() as c:
        row = c.execute('SELECT * FROM candidates WHERE id=?', (candidate_id,)).fetchone()
        return dict(row) if row else None

def update_candidate(candidate_id, name, email, phone, location):
    with connect() as c:
        c.execute('UPDATE candidates SET full_name=?,email=?,phone=?,location=? WHERE id=?',
                  (name.strip(),email.strip(),phone.strip(),location.strip(),candidate_id))

def add_resume(candidate_id, metadata):
    with connect() as c:
        cur = c.execute("""INSERT INTO resumes (candidate_id,filename,file_type,file_size,stored_path)
                           VALUES (?,?,?,?,?)""",
                        (candidate_id,metadata['filename'],metadata['file_type'],
                         metadata['file_size'],metadata['stored_path']))
        return cur.lastrowid

def resumes(candidate_id):
    with connect() as c:
        return [dict(r) for r in c.execute(
            'SELECT * FROM resumes WHERE candidate_id=? ORDER BY id DESC', (candidate_id,))]

def save_extraction(candidate_id, result):
    with connect() as c:
        c.execute("""UPDATE candidates SET summary=?,skills=?,education=?,experience=?,
                     projects=?,certifications=? WHERE id=?""",
                  (result['summary'],json.dumps(result['skills']),json.dumps(result['education']),
                   json.dumps(result['experience']),json.dumps(result['projects']),
                   json.dumps(result['certifications']),candidate_id))
