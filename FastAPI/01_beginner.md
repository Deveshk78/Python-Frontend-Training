# FastAPI — Beginner

Install: `pip install fastapi uvicorn[standard]`
Run any example: `uvicorn filename:app --reload`

## 1. Your first API

```python
# main.py
from fastapi import FastAPI

app = FastAPI(title="Hello FastAPI")

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}
```
Run: `uvicorn main:app --reload` → visit `http://127.0.0.1:8000/docs` for automatic Swagger UI.

## 2. Path parameters & type hints

FastAPI uses Python type hints for validation and docs generation automatically.

```python
@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}
```
`item_id` must be an int — FastAPI returns `422 Unprocessable Entity` automatically if not.

## 3. Query parameters

```python
@app.get("/users")
def list_users(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}
```
Call: `GET /users?skip=5&limit=20`

## 4. Request body with Pydantic models

```python
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    price: float
    in_stock: bool = True

@app.post("/items")
def create_item(item: Item):
    return {"received": item}
```
Pydantic validates the JSON body and gives you a typed Python object.

## 5. HTTP methods (CRUD basics)

```python
items_db: dict[int, Item] = {}

@app.post("/items/{item_id}")
def upsert_item(item_id: int, item: Item):
    items_db[item_id] = item
    return item

@app.get("/items/{item_id}")
def get_item(item_id: int):
    return items_db.get(item_id, {"error": "not found"})

@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    return {"deleted": items_db.pop(item_id, None) is not None}
```

## 6. Status codes & error handling

```python
from fastapi import HTTPException, status

@app.get("/items/{item_id}/strict")
def get_item_strict(item_id: int):
    if item_id not in items_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return items_db[item_id]
```

## 7. Automatic docs

- `/docs` — Swagger UI
- `/redoc` — ReDoc
Both are generated from your type hints and Pydantic models — no extra work needed.

## 8. Path operation order matters

```python
@app.get("/users/me")     # must come before /users/{user_id}
def get_current_user():
    return {"user": "me"}

@app.get("/users/{user_id}")
def get_user(user_id: str):
    return {"user_id": user_id}
```

## Practice exercises
1. Build a `/greet/{name}` endpoint returning `{"greeting": f"Hello {name}"}`.
2. Add a `Book` Pydantic model (title, author, year) and a POST `/books` endpoint.
3. Add query params `search` and `limit` to filter a static in-memory list of books.
4. Return `404` when a book id doesn't exist.
