# Streamlit — Beginner

Install: `pip install streamlit`
Run: `streamlit run app.py`

## 1. Your first app

```python
# app.py
import streamlit as st

st.title("Hello Streamlit")
st.write("This is my first app!")
```

## 2. Text elements

```python
st.header("Header")
st.subheader("Subheader")
st.markdown("**Bold** and _italic_ text, and `code`")
st.code("print('hello')", language="python")
st.latex(r"e^{i\pi} + 1 = 0")
```

## 3. Widgets & interactivity

```python
name = st.text_input("Your name")
age = st.slider("Age", 0, 100, 25)
agree = st.checkbox("I agree")
option = st.selectbox("Pick one", ["A", "B", "C"])

if st.button("Submit"):
    st.write(f"Hello {name}, age {age}, chose {option}")
```
Every widget interaction triggers a full script rerun from top to bottom — this is the core Streamlit execution model.

## 4. Displaying data

```python
import pandas as pd

df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
st.dataframe(df)
st.table(df)
st.line_chart(df)
st.bar_chart(df)
```

## 5. Layout basics

```python
col1, col2 = st.columns(2)
with col1:
    st.write("Left")
with col2:
    st.write("Right")

with st.sidebar:
    st.write("Sidebar content")

with st.expander("Show details"):
    st.write("Hidden content revealed")
```

## 6. Session state (persisting values across reruns)

```python
if "counter" not in st.session_state:
    st.session_state.counter = 0

if st.button("Increment"):
    st.session_state.counter += 1

st.write(f"Count: {st.session_state.counter}")
```

## 7. File upload & images

```python
uploaded = st.file_uploader("Upload a CSV", type=["csv"])
if uploaded is not None:
    df = pd.read_csv(uploaded)
    st.dataframe(df)

st.image("https://placekitten.com/300/200", caption="A kitten")
```

## Practice exercises
1. Build a BMI calculator: `st.number_input` for weight/height, compute and `st.metric` the result.
2. Build a CSV uploader that shows `st.dataframe`, `df.describe()`, and a `st.line_chart` of a chosen numeric column.
3. Use `st.session_state` to build a simple to-do list (add/remove items) that persists across reruns.
