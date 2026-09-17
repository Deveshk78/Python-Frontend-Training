# Streamlit — Advanced

## 1. Streamlit execution model deep-dive

Every user interaction reruns the **entire script top-to-bottom**. Key implications:
- Expensive computations must be cached (`@st.cache_data`/`@st.cache_resource`) or gated behind `st.form`/buttons.
- State that must survive reruns goes in `st.session_state`, not plain Python variables.
- Widget keys (`key=...`) let you read/write the same state across reruns and avoid duplicate-ID errors.

## 2. Fragments (partial reruns) — Streamlit 1.33+

```python
@st.fragment(run_every="10s")
def live_metrics():
    st.metric("Active users", get_active_user_count())

live_metrics()  # only this fragment reruns, not the whole page
```
Fragments avoid full-page reruns for expensive dashboards/live-updating widgets — critical for responsive GenAI demo UIs.

## 3. Custom bidirectional components

```python
# Only needed for genuinely custom JS/React widgets; most apps don't need this.
import streamlit.components.v1 as components
components.html("<h3>Custom HTML/JS widget</h3>", height=100)
```
For production custom components, scaffold with `streamlit-component-lib` (React + a Python wrapper using `declare_component`).

## 4. Async / background work patterns

Streamlit's script execution is synchronous per rerun; long-running async work (e.g., calling multiple LLMs concurrently) should be wrapped:

```python
import asyncio

async def call_llms_concurrently(prompts: list[str]):
    async def call_one(p):
        await asyncio.sleep(1)  # replace with real async API call
        return f"response to {p}"
    return await asyncio.gather(*(call_one(p) for p in prompts))

results = asyncio.run(call_llms_concurrently(["a", "b", "c"]))
```

## 5. State management architecture for complex apps

```python
from dataclasses import dataclass, field

@dataclass
class AppState:
    documents: list = field(default_factory=list)
    chat_history: list = field(default_factory=list)

def get_state() -> AppState:
    if "app_state" not in st.session_state:
        st.session_state.app_state = AppState()
    return st.session_state.app_state
```
Centralizing state in a dataclass (rather than scattering dict keys) scales much better for multi-page GenAI apps.

## 6. Performance: fragment isolation + cache invalidation strategy

- Use `st.cache_data(hash_funcs=...)` when caching functions that take un-hashable args (e.g., a custom client object) — pass a hash function or mark param with a leading underscore to skip hashing.
- Invalidate caches explicitly with `.clear()` after data-mutating actions (e.g., re-ingesting documents into a vector store).

```python
@st.cache_resource
def get_vector_store(_embeddings_fn):  # underscore -> not hashed
    return build_faiss_index(_embeddings_fn)
```

## 7. Authentication & access control

Streamlit has no built-in auth. Common approaches:
- `streamlit-authenticator` package (username/password + cookie sessions).
- Reverse proxy with OAuth2 (e.g., oauth2-proxy in front of the app) for enterprise SSO — recommended for internal architect/management demos behind corporate auth.
- Streamlit Community Cloud / Snowflake support native viewer-based access control.

## 8. Deployment

- **Streamlit Community Cloud**: zero-infra, good for quick demos.
- **Docker + any cloud (Azure Container Apps, AKS, App Service)**: `streamlit run app.py --server.port 8080 --server.address 0.0.0.0 --server.headless true`.
- Put behind Nginx/Traefik for TLS + auth for architect/management-facing demos.
- Set `server.enableCORS`/`server.enableXsrfProtection` correctly when embedding behind a proxy.

## 9. Observability for demo reliability

```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("genai-demo")

try:
    result = run_rag_pipeline(query)
except Exception:
    logger.exception("RAG pipeline failed")
    st.error("Something went wrong generating the answer — check logs.")
```

## Practice exercises
1. Convert a slow polling dashboard section into a `@st.fragment(run_every=...)`.
2. Refactor scattered `st.session_state["x"]` keys into a single `AppState` dataclass.
3. Add `streamlit-authenticator` login gating access to an internal-only page.
4. Containerize a Streamlit app with a `Dockerfile` and run it with `--server.headless true`.
