# Streamlit — Intermediate

## 1. Multi-page apps

```
app.py
pages/
  1_📊_Dashboard.py
  2_⚙️_Settings.py
```
Files in `pages/` automatically appear as separate navigable pages in the sidebar. (Streamlit 1.36+ also supports `st.navigation`/`st.Page` for programmatic multi-page apps.)

```python
# main.py (new-style navigation)
import streamlit as st

dashboard = st.Page("pages/dashboard.py", title="Dashboard", icon="📊")
settings = st.Page("pages/settings.py", title="Settings", icon="⚙️")
pg = st.navigation([dashboard, settings])
pg.run()
```

## 2. Caching for performance

```python
@st.cache_data(ttl=600)
def load_data(path: str) -> pd.DataFrame:
    return pd.read_csv(path)

@st.cache_resource
def get_model():
    return load_expensive_ml_model()
```
`cache_data` is for serializable data (DataFrames, lists); `cache_resource` is for singletons (DB connections, ML models, clients) that shouldn't be copied/pickled.

## 3. Forms (batch input, avoids rerun-per-keystroke)

```python
with st.form("my_form"):
    name = st.text_input("Name")
    submitted = st.form_submit_button("Submit")
    if submitted:
        st.write(f"Hello {name}")
```

## 4. Custom components & advanced widgets

```python
tab1, tab2 = st.tabs(["Chart", "Data"])
with tab1:
    st.line_chart(df)
with tab2:
    st.dataframe(df)

st.plotly_chart(fig)   # Plotly integration
st.pydeck_chart(deck)  # Maps
```

## 5. Chat UI primitives (used heavily for GenAI apps)

```python
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask me anything"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    response = f"Echo: {prompt}"  # replace with real LLM call
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)
```

## 6. Streaming responses (great for LLM token-by-token output)

```python
def stream_tokens():
    for word in "This is a streamed response from an LLM".split():
        yield word + " "

with st.chat_message("assistant"):
    st.write_stream(stream_tokens())
```

## 7. Secrets management

```toml
# .streamlit/secrets.toml
[api]
anthropic_key = "sk-..."
```
```python
api_key = st.secrets["api"]["anthropic_key"]
```

## 8. Connecting to databases

```python
conn = st.connection("sql", type="sql")
df = conn.query("SELECT * FROM users LIMIT 10")
```

## 9. Custom theming

```toml
# .streamlit/config.toml
[theme]
primaryColor = "#4F8BF9"
backgroundColor = "#0E1117"
textColor = "#FAFAFA"
font = "sans serif"
```

## Practice exercises
1. Build a 3-page app (`Home`, `Upload`, `Results`) using `st.navigation`/`st.Page`.
2. Cache a slow data-loading function with `st.cache_data` and verify it isn't recomputed on rerun.
3. Build a mock chat UI using `st.chat_message`/`st.chat_input` with a streamed fake response.
4. Store an API key in `.streamlit/secrets.toml` and read it via `st.secrets`.
