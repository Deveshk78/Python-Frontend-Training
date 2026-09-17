# Capstone SaaS Project — Generative AI RAG Platform (Streamlit Front End)

A demo-ready SaaS reference implementation showing a Streamlit front end for a generative
AI backend built with **AutoGen** (multi-agent orchestration), **Claude Sonnet**, **BM25**,
**HuggingFaceInferenceAPIEmbeddings**, **Cosmos DB**, and **FAISS**, implementing five RAG
architectures: **Fusion, Speculative, Graph, Temporal, and Agentic RAG**.

## Why this is safe to demo to architects/management today

Every external dependency has a transparent, deterministic **offline fallback**:

| Component | Live implementation | Offline demo fallback |
|---|---|---|
| LLM | Claude Sonnet (`anthropic` SDK) | Deterministic extractive "synthetic answer" generator |
| Embeddings | `HuggingFaceInferenceAPIEmbeddings` | Local hashing-based pseudo-embedding |
| Vector store | FAISS (`IndexFlatIP`) | NumPy cosine-similarity fallback (same math) |
| Persistence | Azure Cosmos DB | In-memory dict store |
| Multi-agent | AutoGen (`pyautogen`) | Sequential simulation of the same agent roles |

Set `DEMO_MODE=true` (default, see `.env.example`) to force every component into
offline/demo mode regardless of installed packages/keys — guaranteed to run standalone.
Set `DEMO_MODE=false` and populate real credentials to run fully live.

## Quick start

```bash
cd Capstone-SaaS-RAG
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
copy .env.example .env        # then optionally fill in real API keys
streamlit run app.py
```

Open the sidebar to navigate:
1. **Fusion RAG** — BM25 + FAISS combined via Reciprocal Rank Fusion.
2. **Speculative RAG** — parallel draft generation + verification.
3. **Graph RAG** — vector seed + knowledge-graph multi-hop expansion.
4. **Temporal RAG** — recency-weighted re-ranking for conflicting sources.
5. **Agentic RAG** — Planner → Retriever-Critic → Writer → Critic multi-agent loop.
6. **Architecture Dashboard** — run one question through all 5 strategies side-by-side,
   with latency charts and retrieval overlap — the recommended page for live demos.

## Project layout

```
Capstone-SaaS-RAG/
  app.py                       # Streamlit entry point (Home)
  pages/                       # auto-discovered Streamlit multi-page app
    1_🔀_Fusion_RAG.py
    2_⚡_Speculative_RAG.py
    3_🕸️_Graph_RAG.py
    4_🕰️_Temporal_RAG.py
    5_🤖_Agentic_RAG.py
    6_📊_Architecture_Dashboard.py
  frontend/
    ui_helpers.py               # shared rendering: status badges, answer/metrics panels
  backend/
    config.py                   # pydantic-settings, .env driven, demo-mode aware
    embeddings.py                # HuggingFaceInferenceAPIEmbeddings wrapper + fallback
    llm_client.py                 # Claude Sonnet wrapper + fallback
    data/sample_docs.py            # synthetic enterprise knowledge base (demo corpus)
    retrievers/
      bm25_retriever.py            # BM25 (rank_bm25, with pure-Python fallback)
      faiss_retriever.py            # FAISS (with NumPy fallback)
      cosmos_store.py                # Azure Cosmos DB (with in-memory fallback)
    graph/knowledge_graph.py       # tag-based knowledge graph (networkx)
    agents/autogen_agents.py       # AutoGen-style Planner/Critic/Writer roles
    rag/
      base.py                      # shared RAGResult / RetrieverBundle types
      fusion_rag.py
      speculative_rag.py
      graph_rag.py
      temporal_rag.py
      agentic_rag.py
    utils/metrics.py             # per-stage latency timing used in the UI
  requirements.txt
  .env.example
  .streamlit/config.toml
```

## Demo script suggestion (for an architect/management walkthrough)

1. Open **Home** — show the status badges (all "OFFLINE FALLBACK" in demo mode) and the
   architecture diagram; explain the graceful-degradation design.
2. Open **Architecture Dashboard**, ask one question, and run all five strategies —
   point out the latency chart differences and how each strategy grounds its answer
   differently (see the "How this strategy works" caption on each result).
3. Drill into **Agentic RAG** to show the multi-agent transcript (Planner → Critic →
   Writer → final Critic) as a concrete example of AutoGen-style orchestration.
4. Mention the swap-in path to production: flip `DEMO_MODE=false`, provide
   `ANTHROPIC_API_KEY`, `HUGGINGFACEHUB_API_TOKEN`, and `COSMOS_ENDPOINT`/`COSMOS_KEY`
   in `.env` — no code changes required.

## Extending toward production

- Replace `backend/data/sample_docs.py` with a real ingestion pipeline (chunking +
  embedding real documents into Cosmos DB + FAISS/managed vector store).
- Swap the simulated AutoGen roles in `backend/agents/autogen_agents.py` for a real
  `autogen.GroupChat` with Claude-backed `ConversableAgent`s.
- Add authentication (see `Streamlit/03_advanced.md` — reverse proxy SSO or
  `streamlit-authenticator`) before exposing this beyond a local/internal demo.
- Add persistent chat history per user/session in Cosmos DB (`cosmos_store` already
  supports arbitrary document upserts).
