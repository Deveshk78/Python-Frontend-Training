# FastAPI — Interview Questions

## Conceptual

**Q1. What makes FastAPI fast compared to Flask/Django?**
A: It's built on Starlette (ASGI) + Pydantic. ASGI enables native async I/O (non-blocking), and Pydantic uses compiled validation (Rust-based `pydantic-core` in v2), reducing overhead vs WSGI frameworks that are synchronous by default.

**Q2. What is ASGI vs WSGI?**
A: WSGI is a synchronous, single-request-per-thread specification (Flask, Django classic). ASGI supports async/await, WebSockets, and long-lived connections, enabling higher concurrency for I/O-bound workloads.

**Q3. How does FastAPI generate OpenAPI docs automatically?**
A: It introspects Python type hints and Pydantic models on path operations to build a JSON Schema-based OpenAPI spec, served at `/openapi.json`, rendered via Swagger UI (`/docs`) and ReDoc (`/redoc`).

**Q4. Explain `Depends()` and why it's useful.**
A: It's FastAPI's dependency injection system — reusable callables (sync or async, optionally with `yield` for setup/teardown) injected into path operations. Useful for DB sessions, auth, shared validation, and testability (via `dependency_overrides`).

**Q5. Pydantic v1 vs v2 — what changed?**
A: v2 rewrote the core validation engine in Rust (`pydantic-core`), giving 5-50x speedups; `@validator` → `@field_validator`, `.dict()` → `.model_dump()`, config via `model_config` instead of inner `Config` class.

**Q6. How do you handle background work without blocking the response?**
A: `BackgroundTasks` for lightweight fire-and-forget work in-process; for heavier/distributed work use Celery/RQ/Arq with a message broker (Redis/RabbitMQ).

**Q7. Sync vs async path operations — when to use `def` vs `async def`?**
A: Use `async def` when calling async I/O (async DB drivers, httpx async client). Use plain `def` for CPU-bound or blocking sync calls — FastAPI runs those in a thread pool automatically so they don't block the event loop.

**Q8. How does FastAPI validate request bodies vs query/path params?**
A: Pydantic `BaseModel` subclasses in the signature are parsed from the JSON body; primitives (`int`, `str`, etc.) are parsed from path/query params unless explicitly marked `Body(...)`.

**Q9. What's the purpose of `response_model`?**
A: Filters/validates/documents the *output* shape independent of what the function returns — e.g., stripping sensitive fields like passwords, and generating accurate OpenAPI schemas.

**Q10. How would you version a FastAPI API?**
A: URL-path versioning (`/v1/...` via separate `APIRouter`s with prefixes), header-based versioning, or separate `FastAPI()` sub-apps mounted at different paths.

## Coding / scenario

**Q11.** Write a dependency that validates an API key from a header and raises `401` if missing/invalid.
```python
from fastapi import Header, HTTPException

def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != "expected-key":
        raise HTTPException(status_code=401, detail="Invalid API key")
```

**Q12.** How do you test an endpoint that depends on a database without hitting a real DB?
A: Use `app.dependency_overrides[get_db] = lambda: fake_db_session` in tests with `TestClient`, or use an in-memory SQLite engine.

**Q13.** How would you implement pagination for a large list endpoint?
A: Query params `skip`/`limit` (offset pagination) or cursor-based pagination using an opaque token encoding the last seen ID — cursor-based is preferred for large/changing datasets to avoid skip-based performance degradation.

**Q14.** Your endpoint needs to call three independent external APIs — how do you avoid serial latency?
A: Use `httpx.AsyncClient` and `asyncio.gather()` to issue calls concurrently inside an `async def` path operation.

**Q15.** How do you prevent duplicate request bodies being read twice (e.g., in middleware + route)?
A: Starlette caches the body after the first `await request.body()` call, so subsequent reads return the cached bytes — but be cautious with streaming bodies and large payloads.

**Q16.** Explain how you'd add global exception handling for unhandled exceptions in production.
A: Register `@app.exception_handler(Exception)` to catch anything unhandled, log it with a correlation/request ID, and return a generic `500` without leaking internals.

**Q17.** What's the difference between `Path`, `Query`, and `Body` parameter functions?
A: They explicitly declare where a parameter is read from and let you add metadata/validation (e.g., `Query(default=10, ge=1, le=100)`), useful when the default inference (path/query/body) isn't what you want.

**Q18.** How would you deploy a FastAPI app for high availability?
A: Multiple Uvicorn workers behind Gunicorn (or run several containers) behind a load balancer, with health checks, horizontal autoscaling (K8s HPA), and readiness/liveness probes.
