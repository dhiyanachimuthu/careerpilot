# CareerPilot — Infosys Virtual Internship Milestone 1

A student profile and AI-powered resume understanding prototype.

## Run on Windows (VS Code CMD terminal)

```cmd
py -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m streamlit run app.py
```

Open http://localhost:8501. To test the hosted LLM, obtain a Groq API key at
https://console.groq.com/keys and paste it into the AI Resume Extraction page.
Do not put the key in source code or GitHub.

## Milestone coverage

- M1.1: `docs/RESEARCH.md` — workflows, RAG, multi-agent patterns, choices.
- M1.2: `docs/ARCHITECTURE.md` — Mermaid diagram, six agents, data schema, flow.
- M1.3: Profile create/edit, resume upload and persisted file metadata.
- M1.4: PDF/DOCX/TXT parsing, Groq-hosted LLM extraction, Pydantic validation,
  SQLite persistence, synthetic sample resumes and tests.
- Tech stack: `docs/TECH_STACK.md`.

## Demonstration

1. Create a profile.
2. Upload `samples/student_data.txt` under Upload Resume.
3. View Profiles → Uploaded resume metadata.
4. AI Resume Extraction → choose profile, paste Groq key, upload same sample,
   click Extract and save profile.
5. View Profiles → verify saved skills, education, experience and projects.
6. Repeat with other samples; review results for factual correctness.

## Automated tests

```cmd
.venv\Scripts\python.exe -m pytest -q
```

Tests cover database, TXT/PDF/DOCX parsing and schema validation.
**They do not replace a live LLM integration test.**

## Submit to GitHub

Confirm `.gitignore` excludes `uploads/`, `data/`, `.env`, `.venv/`.
Then run `git init`, `git add .`, `git commit -m "Milestone 1"`,
`git branch -M main`, `git remote add origin YOUR_REPO_URL`, `git push -u origin main`.
Submit the actual GitHub URL, architecture and tech stack.

## Limitations

Local prototype; no authentication; scanned PDFs need OCR; live LLM needs
internet and an API key; job RAG and six agent executions are designed for
future milestones, not falsely claimed as operational.
