# M1.1 Research and Technical Understanding

## Internship application workflow

Student registration → profile creation → resume upload → resume parsing →
job discovery → eligibility checks → job-resume matching → skill gap review →
resume/cover-letter tailoring → interview preparation → application submission →
status tracking. M1 implements the candidate understanding foundation only.

## Retrieval-Augmented Generation (RAG)

A RAG system ingests trusted job descriptions, cleans and chunks documents,
creates embeddings, stores them in a vector database, retrieves relevant chunks
for a user query, and supplies those chunks with provenance to an LLM.
For CareerPilot, job requirements retrieved from the knowledge base would inform
matching and skill-gap agents. RAG can improve grounding but does not guarantee
correctness. Future stack: ChromaDB, embedding model, retrieval filters, citations.

## Multi-agent design patterns

**Supervisor/router:** a Career Assistant delegates to specialized agents.
**Sequential pipeline:** matching → gap analysis → preparation tasks.
**Shared state:** all agents consume the same versioned candidate profile.
**Human-in-the-loop:** student approves edits and applications.
**Guardrails:** agents cannot invent skills, work history or submitted applications.
LangGraph is a potential future orchestration framework, not an M1 dependency.

## LLM structured extraction

Text extraction (PyMuPDF/python-docx) differs from semantic information extraction.
The hosted LLM maps unstructured resume text into a typed JSON schema; Pydantic
validates the returned structure. Validation checks shape, not factual accuracy.
Missing information must remain empty. Human review is recommended.

## Security, privacy and limitations

Uploaded resumes contain personal data. The prototype stores files locally,
excludes them from Git, and only sends resume text to the hosted Groq API after
an explicit user action. No user authentication, encryption-at-rest or OCR yet.
Model availability, quotas, latency, and extraction accuracy vary.

## Technical references

- https://docs.streamlit.io/
- https://pymupdf.readthedocs.io/
- https://python-docx.readthedocs.io/
- https://docs.pydantic.dev/
- https://console.groq.com/docs/openai
- https://python.langchain.com/docs/concepts/rag/
- https://langchain-ai.github.io/langgraph/
