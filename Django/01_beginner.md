# Django — Beginner

Install: `pip install django`
Start project: `django-admin startproject mysite .`
Start app: `python manage.py startapp blog`

## 1. Project vs app structure

```
mysite/          # project config (settings.py, urls.py, wsgi.py)
blog/            # a reusable "app" (models, views, urls, admin)
manage.py
```

## 2. Your first view

```python
# blog/views.py
from django.http import JsonResponse

def home(request):
    return JsonResponse({"message": "Hello, Django!"})
```

```python
# blog/urls.py
from django.urls import path
from . import views

urlpatterns = [path("", views.home, name="home")]

# mysite/urls.py
from django.urls import path, include
urlpatterns = [path("", include("blog.urls"))]
```

Run: `python manage.py runserver`

## 3. Models & the ORM

```python
# blog/models.py
from django.db import models

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
```

```bash
python manage.py makemigrations
python manage.py migrate
```

## 4. Django admin

```python
# blog/admin.py
from django.contrib import admin
from .models import Post

admin.site.register(Post)
```
Create a superuser: `python manage.py createsuperuser` → visit `/admin`.

## 5. Templates

```python
# settings.py: TEMPLATES[0]["DIRS"] = [BASE_DIR / "templates"]

# blog/views.py
from django.shortcuts import render

def post_list(request):
    posts = Post.objects.all()
    return render(request, "blog/post_list.html", {"posts": posts})
```
```html
<!-- templates/blog/post_list.html -->
<ul>
{% for post in posts %}
  <li>{{ post.title }}</li>
{% endfor %}
</ul>
```

## 6. Forms

```python
from django import forms

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "content"]
```

## 7. QuerySets basics

```python
Post.objects.all()
Post.objects.filter(title__icontains="django")
Post.objects.get(id=1)
Post.objects.order_by("-created_at")[:5]
Post.objects.create(title="New", content="...")
```

## 8. Static files

`settings.py`: `STATIC_URL = "static/"`; place files in `<app>/static/<app>/...` and reference with `{% load static %}{% static "blog/style.css" %}`.

## Practice exercises
1. Create a `Comment` model with a `ForeignKey` to `Post` and register both in the admin.
2. Build a `post_detail` view + template rendering a single post by `pk`.
3. Add a `PostForm`-based create view that saves a new `Post` on POST.
4. Add filtering via a `?q=` query param using `Post.objects.filter(title__icontains=q)`.
