# Milestone 1 Tech Stack

| Component | Selected technology | Status / rationale |
|---|---|---|
| UI | Streamlit | Implemented; quick Python interface |
| Backend | Python | Implemented; app logic and validation |
| Database | SQLite | Implemented; persistent candidate and resume metadata |
| Resume file storage | Local uploads/ | Implemented; randomized filenames |
| PDF parser | PyMuPDF | Implemented; text-based PDFs |
| DOCX parser | python-docx | Implemented; paragraphs and tables |
| TXT parser | Python UTF-8 | Implemented |
| LLM | Groq-hosted Llama 3.3 70B | Implemented; live API test requires user's key |
| Schema validation | Pydantic | Implemented; structured fields |
| RAG | ChromaDB + embeddings | Planned, not claimed implemented |
| Multi-agent coordination | LangGraph | Planned, not claimed implemented |
| Application tracking | SQLite extension | Planned |
| Version control | Git/GitHub | User publishes repository |

The model and free-tier availability may change. Do not publish secrets or real resumes.
