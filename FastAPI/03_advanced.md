# FastAPI — Advanced

## 1. Advanced dependency injection (yield + sub-dependencies + caching)

```python
from fastapi import Depends
from contextlib import asynccontextmanager

class DBSessionManager:
    def __init__(self):
        self.pool = None

    async def connect(self):
        self.pool = "pool-object"

    async def disconnect(self):
        self.pool = None

db_manager = DBSessionManager()

@asynccontextmanager
async def lifespan(app):
    await db_manager.connect()
    yield
    await db_manager.disconnect()

app = FastAPI(lifespan=lifespan)

async def get_session():
    yield db_manager.pool
```
`lifespan` replaces the deprecated `@app.on_event("startup"/"shutdown")`.

## 2. WebSockets

```python
from fastapi import WebSocket, WebSocketDisconnect

connections: list[WebSocket] = []

@app.websocket("/ws/chat")
async def chat(ws: WebSocket):
    await ws.accept()
    connections.append(ws)
    try:
        while True:
            msg = await ws.receive_text()
            for conn in connections:
                await conn.send_text(msg)
    except WebSocketDisconnect:
        connections.remove(ws)
```

## 3. Custom exception handlers

```python
from fastapi.requests import Request
from fastapi.responses import JSONResponse

class DomainError(Exception):
    def __init__(self, message: str):
        self.message = message

@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError):
    return JSONResponse(status_code=400, content={"error": exc.message})
```

## 4. Response models, response_model_exclude, and versioning

```python
from pydantic import BaseModel

class UserOut(BaseModel):
    id: int
    username: str
    # password intentionally excluded from output

@app.get("/users/{id}", response_model=UserOut)
def get_user(id: int):
    return {"id": id, "username": "alice", "password": "secret"}  # password stripped automatically
```

## 5. Rate limiting & security headers (production hardening)

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/limited")
@limiter.limit("5/minute")
def limited_endpoint(request: Request):
    return {"ok": True}
```

## 6. Async SQLAlchemy 2.0 with connection pooling

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/db", pool_size=20)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_session():
    async with async_session() as session:
        yield session
```

## 7. Structured logging & observability (OpenTelemetry)

```python
import logging
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

FastAPIInstrumentor.instrument_app(app)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
```

## 8. Multi-tenant / dynamic routing with `APIRouter` + dependency overrides

```python
def get_tenant_id(x_tenant_id: str = Header(...)) -> str:
    return x_tenant_id

@app.get("/data")
def get_data(tenant_id: str = Depends(get_tenant_id)):
    return {"tenant": tenant_id}

# In tests: app.dependency_overrides[get_tenant_id] = lambda: "test-tenant"
```

## 9. Production deployment checklist

- Run behind Gunicorn + Uvicorn workers: `gunicorn -k uvicorn.workers.UvicornWorker -w 4 main:app`
- Set `docs_url=None, redoc_url=None` in prod if the API is internal-only.
- Enable `GZipMiddleware` for large responses.
- Use `orjson` response class for faster JSON serialization.
- Add health (`/healthz`) and readiness (`/readyz`) probes for Kubernetes.
- Pin dependency versions; run `pip-audit` in CI.

## 10. Streaming responses (for LLM token streaming — used in the capstone project)

```python
from fastapi.responses import StreamingResponse

async def token_generator():
    for token in ["Hello", " ", "world"]:
        yield token

@app.get("/stream")
async def stream():
    return StreamingResponse(token_generator(), media_type="text/plain")
```

## Practice exercises
1. Add a WebSocket endpoint that streams incrementing numbers every second until the client disconnects.
2. Implement a custom `RateLimitExceeded` exception with a handler returning `429`.
3. Wire up async SQLAlchemy with a `Depends`-based session and write an endpoint using it.
4. Add OpenTelemetry tracing and export spans to console for one endpoint.
