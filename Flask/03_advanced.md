# Flask — Advanced

## 1. Application context vs request context internals

Flask maintains two context stacks: the **application context** (`current_app`, `g`) and the **request context** (`request`, `session`). Understanding push/pop order matters for testing, CLI commands, and background jobs that run outside a request.

```python
with app.app_context():
    # current_app, g available; request is NOT
    db.create_all()

with app.test_request_context("/items?q=1"):
    # request, session available
    print(request.args.get("q"))
```

## 2. Custom CLI commands

```python
import click

@app.cli.command("seed-db")
def seed_db():
    db.session.add(User(username="admin"))
    db.session.commit()
    click.echo("Seeded.")
```
Run: `flask seed-db`

## 3. Signals (Blinker) for decoupled side effects

```python
from flask import request_started, request_finished

def log_request(sender, **extra):
    sender.logger.info("Request started")

request_started.connect(log_request, app)
```

## 4. Custom error handling & structured logging

```python
import logging
from flask.logging import default_handler

app.logger.removeHandler(default_handler)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
app.logger.addHandler(handler)

@app.errorhandler(Exception)
def handle_unexpected(e):
    app.logger.exception("Unhandled error")
    return {"error": "internal server error"}, 500
```

## 5. Async views (Flask 2.x+, requires `asgiref`)

```python
import httpx

@app.route("/async-demo")
async def async_demo():
    async with httpx.AsyncClient() as client:
        resp = await client.get("https://httpbin.org/get")
        return resp.json()
```
Note: Flask is WSGI at heart — async views run each in an event loop per request but the server itself is still sync; for true async concurrency at scale, prefer FastAPI/Starlette or Quart.

## 6. Extensions architecture — writing your own

```python
class MyExtension:
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.extensions["my_ext"] = self
        app.teardown_appcontext(self.teardown)

    def teardown(self, exception=None):
        pass
```

## 7. Production deployment

- Serve with Gunicorn: `gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app()"`
- Put Nginx in front for TLS termination and static file serving.
- Set `SESSION_COOKIE_SECURE=True`, `SESSION_COOKIE_HTTPONLY=True`, `PREFERRED_URL_SCHEME=https` in prod config.
- Use `ProxyFix` middleware when behind a reverse proxy so `request.remote_addr`/scheme are correct.

```python
from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)
```

## 8. Performance: connection pooling, N+1 avoidance

```python
# Eager loading to avoid N+1 queries
users = User.query.options(db.joinedload(User.orders)).all()
```

## 9. Security hardening checklist

- Enable CSRF protection (Flask-WTF) on all state-changing forms.
- Use `flask-talisman` for security headers (HSTS, CSP).
- Never render untrusted input with `|safe` in Jinja2 (XSS risk).
- Store secrets in environment variables / a secret manager, never in `config.py` committed to source control.
- Rate-limit auth endpoints with `flask-limiter`.

## Practice exercises
1. Write a custom `flask` CLI command that exports all users to CSV.
2. Add a signal handler that logs request duration using `request_started`/`request_finished`.
3. Wrap the app with `ProxyFix` and set secure cookie flags for a "production" config.
4. Fix an N+1 query by adding `joinedload` and verify with SQLAlchemy echo logging.
