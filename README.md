# Python Web & GenAI Training Workspace

Beginner → Advanced training material and interview prep for **FastAPI**, **Flask**, **Django**, and **Streamlit**, plus a capstone **SaaS Generative AI RAG platform** demoing 5 advanced RAG architectures with a Streamlit front end.

## Structure

```
FastAPI/            Chapters (01_beginner, 02_intermediate, 03_advanced) + interview_questions.md
Flask/               "
Django/               "
Streamlit/             "
Capstone-SaaS-RAG/   Full SaaS demo app (Streamlit UI + AutoGen agents + Fusion/Speculative/Graph/Temporal/Agentic RAG)
```

## How to use the training material

1. Start with `01_beginner` in each framework folder — concepts + runnable code samples.
2. Move to `02_intermediate` then `03_advanced` — each file is self-contained and ordered by increasing complexity.
3. Use `interview_questions.md` in each folder for interview prep (conceptual + coding + scenario questions with answers).
4. Each chapter's code samples are runnable — install the framework (`pip install fastapi uvicorn` / `flask` / `django` / `streamlit`) and run as noted at the top of each file.

## Capstone project

See [Capstone-SaaS-RAG/README.md](Capstone-SaaS-RAG/README.md) for the full generative AI SaaS demo (Streamlit front end, AutoGen multi-agent backend, Claude Sonnet, BM25 + FAISS hybrid retrieval, HuggingFace Inference API embeddings, Cosmos DB persistence) implementing:

- Fusion RAG
- Speculative RAG
- Graph RAG
- Temporal RAG
- Agentic RAG

It runs in a **demo mode** with no external API keys (synthetic in-memory data + local embeddings fallback) so you can present it to architects/management immediately, and switches to full production mode when real keys/services are configured via `.env`.
