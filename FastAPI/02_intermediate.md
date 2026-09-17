# FastAPI — Intermediate

## 1. APIRouter for modular apps

```python
# routers/items.py
from fastapi import APIRouter

router = APIRouter(prefix="/items", tags=["items"])

@router.get("/")
def list_items():
    return []

# main.py
from fastapi import FastAPI
from routers import items

app = FastAPI()
app.include_router(items.router)
```

## 2. Dependency Injection

```python
from fastapi import Depends

def get_db():
    db = {"connected": True}
    try:
        yield db
    finally:
        db["connected"] = False

@app.get("/health")
def health(db: dict = Depends(get_db)):
    return {"db_connected": db["connected"]}
```
Dependencies can be nested, cached per-request, and reused across routes — great for DB sessions, auth, config.

## 3. Pydantic validation (advanced fields)

```python
from pydantic import BaseModel, Field, field_validator

class User(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    age: int = Field(gt=0, le=120)
    email: str

    @field_validator("email")
    @classmethod
    def email_must_contain_at(cls, v: str) -> str:
        if "@" not in v:
            raise ValueError("invalid email")
        return v
```

## 4. Authentication with OAuth2 + JWT

```python
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from datetime import datetime, timedelta

SECRET_KEY = "change-me"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, expires_minutes: int = 30):
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=expires_minutes)
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

@app.get("/me")
def read_current_user(token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    return {"user": payload.get("sub")}
```

## 5. Middleware & CORS

```python
from fastapi.middleware.cors import CORSMiddleware
import time

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

@app.middleware("http")
async def add_process_time_header(request, call_next):
    start = time.time()
    response = await call_next(request)
    response.headers["X-Process-Time"] = str(time.time() - start)
    return response
```

## 6. Async endpoints & background tasks

```python
from fastapi import BackgroundTasks
import asyncio

async def send_notification(email: str):
    await asyncio.sleep(1)
    print(f"Sent email to {email}")

@app.post("/signup")
async def signup(email: str, tasks: BackgroundTasks):
    tasks.add_task(send_notification, email)
    return {"status": "signup queued"}
```

## 7. Database integration with SQLAlchemy (sync) or SQLModel

```python
from sqlmodel import SQLModel, Field, create_engine, Session

class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str

engine = create_engine("sqlite:///heroes.db")
SQLModel.metadata.create_all(engine)

@app.post("/heroes")
def create_hero(hero: Hero):
    with Session(engine) as session:
        session.add(hero)
        session.commit()
        session.refresh(hero)
        return hero
```

## 8. File uploads & responses

```python
from fastapi import UploadFile, File
from fastapi.responses import FileResponse

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    return {"filename": file.filename, "size": len(contents)}
```

## 9. Testing with TestClient

```python
from fastapi.testclient import TestClient

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
```

## Practice exercises
1. Split a To-Do app into `routers/todos.py` with its own `APIRouter`.
2. Add a `get_current_user` dependency that validates a bearer token, and protect one route with it.
3. Add a background task that logs every created item to a file asynchronously.
4. Write 3 `TestClient` tests covering happy path, validation error, and 404.
