# Flask — Intermediate

## 1. Application factory pattern

```python
# app/__init__.py
from flask import Flask

def create_app(config_object="config.DevConfig"):
    app = Flask(__name__)
    app.config.from_object(config_object)

    from app.routes.users import users_bp
    app.register_blueprint(users_bp)

    return app
```
This avoids circular imports and allows multiple app instances (testing, dev, prod).

## 2. Configuration management

```python
# config.py
class BaseConfig:
    DEBUG = False
    SECRET_KEY = "override-in-env"

class DevConfig(BaseConfig):
    DEBUG = True

class ProdConfig(BaseConfig):
    SECRET_KEY = None  # loaded from environment
```

## 3. Flask-SQLAlchemy ORM

```python
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)

# in create_app():
db.init_app(app)
with app.app_context():
    db.create_all()
```

## 4. Flask-Migrate for schema migrations

```bash
pip install Flask-Migrate
flask db init
flask db migrate -m "create users table"
flask db upgrade
```

## 5. Flask-WTF forms with CSRF protection

```python
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired

class SignupForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])

@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        return {"created": form.username.data}
    return render_template("signup.html", form=form)
```

## 6. Authentication with Flask-Login

```python
from flask_login import LoginManager, UserMixin, login_user, login_required

login_manager = LoginManager()

class AppUser(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return AppUser(user_id)

@app.route("/dashboard")
@login_required
def dashboard():
    return {"secure": True}
```

## 7. RESTful APIs with Flask-RESTful / Marshmallow schemas

```python
from marshmallow import Schema, fields, ValidationError

class ItemSchema(Schema):
    name = fields.Str(required=True)
    price = fields.Float(required=True)

@app.route("/items", methods=["POST"])
def create_item():
    try:
        data = ItemSchema().load(request.get_json())
    except ValidationError as err:
        return {"errors": err.messages}, 400
    return {"created": data}, 201
```

## 8. Testing with pytest and Flask test client

```python
import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app("config.TestConfig")
    return app.test_client()

def test_home(client):
    resp = client.get("/")
    assert resp.status_code == 200
```

## 9. Caching with Flask-Caching

```python
from flask_caching import Cache

cache = Cache(config={"CACHE_TYPE": "SimpleCache"})

@app.route("/expensive")
@cache.cached(timeout=60)
def expensive_computation():
    return {"result": sum(range(10_000_000))}
```

## Practice exercises
1. Convert a single-file app into the application factory pattern with `DevConfig`/`TestConfig`.
2. Add a `User` SQLAlchemy model + Flask-Migrate initial migration.
3. Protect a `/profile` route with Flask-Login, redirecting unauthenticated users to `/login`.
4. Add Marshmallow validation to a `POST /orders` endpoint and write a pytest test for the 400 case.
