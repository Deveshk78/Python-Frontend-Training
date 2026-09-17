# Streamlit — Interview Questions

## Conceptual

**Q1. Describe Streamlit's execution model.**
A: On every user interaction (widget change, button click), Streamlit reruns the entire Python script top to bottom. Widgets return their current value inline; there's no separate callback/event-loop model like traditional web frameworks (though `on_click`/`on_change` callbacks exist for pre-rerun side effects).

**Q2. Why and when do you use `st.session_state`?**
A: Local variables are recreated on every rerun and lost. `st.session_state` is a dict-like object that persists across reruns within a user session, needed for things like counters, chat history, or multi-step wizards.

**Q3. Difference between `st.cache_data` and `st.cache_resource`?**
A: `cache_data` serializes/copies the return value (safe for DataFrames, lists, JSON-like data) and is invalidated by input hash changes. `cache_resource` returns the *same object* (no copy/serialization) — used for things that shouldn't be duplicated or aren't picklable: DB connections, ML models, API clients.

**Q4. How do Streamlit fragments differ from a normal rerun?**
A: `@st.fragment` marks a function whose reruns are isolated from the rest of the page — interacting with a widget inside a fragment (or a `run_every` timer) reruns only that fragment, not the entire script, improving performance for partial/live updates.

**Q5. How would you handle multi-page navigation in Streamlit?**
A: Either the file-based `pages/` folder convention (auto-detected) or the newer programmatic `st.Page` + `st.navigation` API, which additionally supports dynamic page lists (e.g., role-based visibility).

**Q6. What are the limitations of Streamlit for production apps?**
A: No built-in authentication/authorization, full-script reruns can be inefficient without careful caching/fragments, limited fine-grained UI control compared to React, and it's fundamentally single-session-per-browser-tab stateful, which complicates horizontal scaling of long-lived state without external storage.

**Q7. How do you stream LLM responses token-by-token in Streamlit?**
A: `st.write_stream(generator)` inside a `st.chat_message` block consumes a generator/iterator (or an OpenAI/Anthropic streaming response object) and renders tokens incrementally as they arrive.

## Coding / scenario

**Q8.** A dashboard recomputes an expensive aggregation on every widget interaction — how do you fix it?
A: Wrap the aggregation function with `@st.cache_data` (keyed on its inputs) so unrelated widget reruns reuse the cached result; only truly changed inputs trigger recomputation.

**Q9.** You need to hold a FAISS index in memory across reruns without rebuilding it each time — which caching decorator, and why?
A: `@st.cache_resource`, because the FAISS index is a stateful in-memory object that shouldn't be serialized/copied.

**Q10.** How would you secure a Streamlit app for internal-only access (e.g., to show architects/management) without building a full auth system?
A: Put it behind a reverse proxy with SSO/OAuth2 (e.g., oauth2-proxy, Azure AD App Proxy), or use `streamlit-authenticator` for a lightweight login gate, and restrict network access via VPN/private endpoint.

**Q11.** How do you avoid duplicate widget key errors when generating widgets in a loop?
A: Pass a unique `key=f"item_{i}"` to each widget instance so Streamlit can distinguish them across reruns.

**Q12.** How would you show live-updating metrics (e.g., token usage counters during a RAG demo) without reloading the whole page?
A: Use `@st.fragment(run_every="2s")` (or manually rerun a fragment) so only the metrics widget updates, keeping the rest of the UI (chat history, sidebar) stable.
