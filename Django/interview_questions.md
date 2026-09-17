# Django — Interview Questions

## Conceptual

**Q1. Explain Django's MVT pattern vs traditional MVC.**
A: Model-View-Template. The "View" in Django is actually the controller (handles request logic), and the "Template" is the presentation layer (equivalent to MVC's View). Django itself handles URL routing → View → Model/Template, acting as the framework's own "controller".

**Q2. What are migrations and how do they work?**
A: Migrations are version-controlled Python files describing schema changes derived from model changes (`makemigrations`), applied to the DB via `migrate`. Django tracks applied migrations in the `django_migrations` table to know current schema state per app.

**Q3. `select_related` vs `prefetch_related` — when to use each?**
A: `select_related` performs a SQL JOIN for ForeignKey/OneToOne (single query, follows single-valued relations). `prefetch_related` issues a separate query per relation and joins in Python — used for ManyToMany and reverse ForeignKey (multi-valued) relations.

**Q4. What is the Django ORM's lazy evaluation?**
A: QuerySets are lazy — they build up a query without hitting the DB until evaluated (iterated, sliced with a concrete index, `list()`, `len()`, etc.), allowing chaining `.filter().exclude().order_by()` efficiently.

**Q5. How does Django's CSRF protection work?**
A: A per-session (or per-request, depending on settings) token is embedded in forms (`{% csrf_token %}`) and validated against a cookie value on unsafe HTTP methods (POST/PUT/DELETE), preventing cross-site form submission attacks.

**Q6. Function-Based Views vs Class-Based Views — trade-offs?**
A: FBVs are explicit and easier to read for simple logic. CBVs (`ListView`, `DetailView`, etc.) reduce boilerplate via inheritance/mixins for common patterns (CRUD, pagination) but can be harder to trace ("where does this behavior come from?") for beginners.

**Q7. What is `settings.py` and how do you manage different environments?**
A: Central configuration module. Common pattern: split into `settings/base.py`, `settings/dev.py`, `settings/prod.py` importing from base, selected via `DJANGO_SETTINGS_MODULE` env var, with secrets pulled from environment variables (`django-environ`).

**Q8. Explain Django signals and a caveat.**
A: Signals (`post_save`, `pre_delete`, etc.) let decoupled code react to model events. Caveat: they can create hidden/implicit side effects that are hard to trace and debug — many teams prefer explicit service-layer calls over signals for critical business logic.

## Coding / scenario

**Q9.** Fix the N+1 query problem: `for post in Post.objects.all(): print(post.author.name)`.
```python
for post in Post.objects.select_related("author").all():
    print(post.author.name)
```

**Q10.** How do you enforce that two DB writes happen atomically or not at all?
A: Wrap in `@transaction.atomic` (or `with transaction.atomic():`), using `select_for_update()` if row-level locking is needed to prevent race conditions.

**Q11.** How would you version a DRF API?
A: URL versioning (`/api/v1/...` via separate routers/serializers), `NamespaceVersioning`, or `AcceptHeaderVersioning` provided by DRF's `DEFAULT_VERSIONING_CLASS` setting.

**Q12.** A view is slow due to a huge queryset being fully serialized — how do you fix it?
A: Add pagination (DRF `PageNumberPagination`/`CursorPagination`), use `.only()`/`.values()` to reduce fetched fields, and add DB indexes on filtered/sorted columns.

**Q13.** How do you run background/async jobs in Django (e.g., sending emails)?
A: Celery + a broker (Redis/RabbitMQ) is the standard; simpler cases can use Django-Q or `django-background-tasks`. Avoid blocking the request/response cycle with slow I/O.

**Q14.** How would you test a view that requires an authenticated user in Django's test framework?
A: `self.client.force_login(user)` (or `login()` with credentials) before making the test request via `self.client.get(...)`.

**Q15.** What's the risk of using mutable default arguments or class-level `objects = []` in Django models, and how does Django's ORM avoid it?
A: Mutable defaults are shared across instances if used as Python default args; Django model fields use `default=` callables (e.g., `default=list` via `JSONField`) or DB-level defaults to avoid shared mutable state across rows.
