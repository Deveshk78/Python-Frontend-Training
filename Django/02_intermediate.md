# Django — Intermediate

## 1. Class-Based Views (CBVs)

```python
from django.views.generic import ListView, DetailView, CreateView
from .models import Post

class PostListView(ListView):
    model = Post
    template_name = "blog/post_list.html"
    context_object_name = "posts"
    paginate_by = 10

class PostDetailView(DetailView):
    model = Post

class PostCreateView(CreateView):
    model = Post
    fields = ["title", "content"]
    success_url = "/posts/"
```

## 2. Django REST Framework (DRF)

```bash
pip install djangorestframework
```
```python
# serializers.py
from rest_framework import serializers
from .models import Post

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["id", "title", "content", "created_at"]

# views.py
from rest_framework import viewsets
from .serializers import PostSerializer

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

# urls.py
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register("posts", PostViewSet)
urlpatterns = [path("api/", include(router.urls))]
```

## 3. Django ORM relationships & advanced querying

```python
class Author(models.Model):
    name = models.CharField(max_length=100)

class Post(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="posts")
    tags = models.ManyToManyField("Tag", blank=True)

# select_related for FK (SQL JOIN), prefetch_related for M2M/reverse FK
Post.objects.select_related("author").prefetch_related("tags").all()

from django.db.models import Count
Author.objects.annotate(post_count=Count("posts")).filter(post_count__gt=5)
```

## 4. Forms validation & ModelForm customization

```python
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "content"]

    def clean_title(self):
        title = self.cleaned_data["title"]
        if len(title) < 5:
            raise forms.ValidationError("Title too short")
        return title
```

## 5. Authentication & permissions

```python
from django.contrib.auth.decorators import login_required
from rest_framework.permissions import IsAuthenticated

@login_required
def dashboard(request):
    ...

class PostViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
```

## 6. Middleware

```python
class RequestTimingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        import time
        start = time.time()
        response = self.get_response(request)
        response["X-Process-Time"] = str(time.time() - start)
        return response
```
Register in `settings.py` → `MIDDLEWARE`.

## 7. Signals

```python
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Post)
def notify_on_new_post(sender, instance, created, **kwargs):
    if created:
        print(f"New post created: {instance.title}")
```

## 8. Celery integration for async tasks

```python
# celery.py
from celery import Celery
app = Celery("mysite", broker="redis://localhost:6379/0")

# tasks.py
@app.task
def send_welcome_email(user_id):
    ...

# view
send_welcome_email.delay(user.id)
```

## 9. Testing

```python
from django.test import TestCase
from .models import Post

class PostModelTest(TestCase):
    def test_str(self):
        post = Post.objects.create(title="Hi", content="...")
        self.assertEqual(str(post), "Hi")
```

## Practice exercises
1. Convert function-based `post_list`/`post_detail` views to `ListView`/`DetailView`.
2. Build a DRF `PostViewSet` with `IsAuthenticated` permission and token auth.
3. Add a `post_save` signal that creates an `AuditLog` entry whenever a `Post` is updated.
4. Write Django `TestCase`s for the model and the DRF endpoint (list + create).
