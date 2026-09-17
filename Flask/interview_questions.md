# Flask — Interview Questions

## Conceptual

**Q1. What is the difference between Flask and Django?**
A: Flask is a micro-framework — minimal core, you choose ORM/auth/admin via extensions. Django is a "batteries included" framework with built-in ORM, admin panel, auth, and forms. Flask offers more flexibility; Django offers more structure/conventions out of the box.

**Q2. Explain the application context and request context.**
A: Flask uses context-local stacks so globals like `current_app`, `g`, `request`, and `session` work correctly per-thread/per-request without passing them explicitly through every function. The app context wraps `current_app`/`g`; the request context (which pushes an app context too) wraps `request`/`session`.

**Q3. What is the application factory pattern and why use it?**
A: A `create_app()` function that builds and returns a configured `Flask` instance. It avoids circular imports, supports multiple configurations (test/dev/prod), and allows creating multiple app instances (useful in testing).

**Q4. How does Flask handle WSGI vs the newer async support?**
A: Flask is fundamentally a WSGI framework (synchronous). Since 2.0, it supports `async def` view functions via `asgiref`'s `async_to_sync`, but the underlying server model is still one-worker-per-request unless you run under an ASGI server with extra shims — it isn't truly async end-to-end like FastAPI/Starlette.

**Q5. What are Blueprints?**
A: A way to organize a Flask app into reusable, modular components (routes, templates, static files) registered on the main app — similar to Django "apps".

**Q6. How do sessions work in Flask by default?**
A: Flask signs session data with `SECRET_KEY` and stores it client-side in a cookie (not server-side by default) — meaning session data is visible (base64) but tamper-proof (signed), so don't store sensitive data in it unless you switch to server-side sessions (e.g., Flask-Session with Redis).

**Q7. How would you prevent CSRF attacks in Flask?**
A: Use Flask-WTF's CSRF protection, which injects and validates a hidden CSRF token on forms; for pure JSON APIs, use token-based auth (JWT/Bearer) instead of cookies, or double-submit cookie pattern.

## Coding / scenario

**Q8.** Write a route that returns 400 if a required JSON field is missing.
```python
@app.route("/orders", methods=["POST"])
def create_order():
    data = request.get_json(silent=True) or {}
    if "item_id" not in data:
        return {"error": "item_id is required"}, 400
    return {"order": data}, 201
```

**Q9.** How do you avoid circular imports between `models.py` and `routes.py`?
A: Use the application factory pattern; instantiate extensions (e.g., `db = SQLAlchemy()`) in a separate module without binding to `app` at import time, then call `db.init_app(app)` inside `create_app()`.

**Q10.** How would you scale a Flask app horizontally, given it's WSGI/sync?
A: Run multiple Gunicorn worker processes (sync or gevent/eventlet workers for I/O-bound loads) behind a load balancer; move CPU-heavy or long-running tasks to background workers (Celery) so request threads aren't blocked.

**Q11.** What's the N+1 query problem and how do you fix it in SQLAlchemy?
A: Lazy-loading related objects triggers one query per parent row. Fix with eager loading (`joinedload`, `selectinload`) to fetch related rows in a single (or few) queries.

**Q12.** How do you test a Flask route that requires authentication?
A: Use the test client to log in first (POST to `/login` to get a session cookie or token), then use that authenticated client/session for subsequent requests; or mock `flask_login.current_user` / override the `login_required` dependency in tests.

**Q13.** Explain `g` and a good use case.
A: `g` is a per-request namespace object for storing data you want to share across functions during a single request (e.g., a DB connection opened once and reused, or a request-scoped cache) without global variables.
