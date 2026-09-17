# Django — Advanced

## 1. Custom user model (do this at project start!)

```python
# accounts/models.py
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    is_premium = models.BooleanField(default=False)

# settings.py
AUTH_USER_MODEL = "accounts.User"
```
Switching later requires a painful migration — always define a custom user model before the first migration in a real project.

## 2. Multi-tenancy strategies

- **Shared DB, tenant column**: every table has a `tenant_id`, enforced via a custom manager/middleware that filters querysets.
- **Schema-per-tenant** (PostgreSQL, `django-tenant-schemas`/`django-tenants`): isolates data at the schema level.
- **DB-per-tenant**: full isolation, more operational overhead, using Django's multi-database routing (`DATABASE_ROUTERS`).

## 3. Custom managers & querysets

```python
class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status="published")

class Post(models.Model):
    status = models.CharField(max_length=20, default="draft")
    objects = models.Manager()
    published = PublishedManager()
```

## 4. Caching strategies

```python
from django.core.cache import cache
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)
def post_list(request):
    ...

def get_popular_posts():
    posts = cache.get("popular_posts")
    if posts is None:
        posts = list(Post.objects.order_by("-views")[:10])
        cache.set("popular_posts", posts, timeout=300)
    return posts
```
Backends: Redis (`django-redis`) recommended for production over `LocMemCache`.

## 5. Database transactions & concurrency

```python
from django.db import transaction

@transaction.atomic
def transfer_funds(from_acc, to_acc, amount):
    from_acc = Account.objects.select_for_update().get(pk=from_acc.pk)
    to_acc = Account.objects.select_for_update().get(pk=to_acc.pk)
    from_acc.balance -= amount
    to_acc.balance += amount
    from_acc.save()
    to_acc.save()
```
`select_for_update()` takes a row lock to prevent race conditions under concurrent writes.

## 6. Async views (Django 4.1+)

```python
import httpx

async def async_view(request):
    async with httpx.AsyncClient() as client:
        resp = await client.get("https://httpbin.org/get")
    return JsonResponse(resp.json())
```
The ORM is still mostly sync — use `sync_to_async` to wrap ORM calls from async views, or the newer async ORM methods (`aget`, `afilter`, etc. in Django 4.1+/5.x).

## 7. Performance profiling & query optimization

- Use `django-debug-toolbar` in dev to spot N+1 queries.
- `django.db.connection.queries` or `django-silk` for profiling in tests.
- Add DB indexes: `class Meta: indexes = [models.Index(fields=["created_at"])]`.
- Use `.only()`/`.defer()` to limit fetched columns for wide tables.

## 8. Security hardening for production

- `DEBUG = False`, proper `ALLOWED_HOSTS`.
- `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE = True`.
- `SECURE_HSTS_SECONDS`, `X_FRAME_OPTIONS = "DENY"`.
- Keep `SECRET_KEY` in environment variables, never in source control.
- Run `python manage.py check --deploy` before shipping.

## 9. Deployment architecture

- ASGI (Daphne/Uvicorn+Gunicorn `uvicorn.workers.UvicornWorker`) for async support, or classic WSGI (Gunicorn) for sync-only apps.
- Static/media files served via WhiteNoise or a CDN/S3, not Django itself, in production.
- Use `django-environ`/`django-configurations` for 12-factor settings management.

## 10. Testing at scale

```python
from django.test import TestCase
from django.test.utils import override_settings

@override_settings(CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}})
class CacheAwareTests(TestCase):
    ...
```
Use `factory_boy` for test data factories and `pytest-django` for faster, fixture-based test suites.

## Practice exercises
1. Add a custom `User` model with an `is_premium` flag and update `AUTH_USER_MODEL`.
2. Implement `select_for_update()` in a funds-transfer function and write a concurrency test.
3. Add a Redis cache backend and cache an expensive aggregate query for 5 minutes.
4. Run `manage.py check --deploy` on a sample project and fix all reported warnings.
