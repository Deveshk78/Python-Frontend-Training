# Flask — Beginner

Install: `pip install flask`
Run: `flask --app main run --debug` or `python main.py`

## 1. Your first app

```python
# main.py
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return {"message": "Hello, Flask!"}

if __name__ == "__main__":
    app.run(debug=True)
```

## 2. Routes, methods and URL variables

```python
@app.route("/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    return {"item_id": item_id}

@app.route("/search")
def search():
    query = request.args.get("q", "")
    return {"query": query}
```
Note: import `request` from `flask`.

## 3. Handling JSON request bodies

```python
from flask import Flask, request, jsonify

@app.route("/items", methods=["POST"])
def create_item():
    data = request.get_json()
    return jsonify({"received": data}), 201
```

## 4. Templates with Jinja2

```python
# templates/index.html
# <h1>Hello {{ name }}</h1>

from flask import render_template

@app.route("/hello/<name>")
def hello(name):
    return render_template("index.html", name=name)
```

## 5. Static files

Place files in `static/` — accessible at `/static/<filename>` automatically.

## 6. Sessions and cookies

```python
from flask import session

app.secret_key = "dev-secret-change-me"

@app.route("/login/<username>")
def login(username):
    session["user"] = username
    return {"logged_in": username}

@app.route("/whoami")
def whoami():
    return {"user": session.get("user")}
```

## 7. Error handling

```python
from flask import abort

@app.route("/items/<int:item_id>/strict")
def get_item_strict(item_id):
    items = {1: "widget"}
    if item_id not in items:
        abort(404)
    return {"item": items[item_id]}

@app.errorhandler(404)
def not_found(e):
    return {"error": "not found"}, 404
```

## 8. Blueprints (basic modularization)

```python
# routes/users.py
from flask import Blueprint

users_bp = Blueprint("users", __name__, url_prefix="/users")

@users_bp.route("/")
def list_users():
    return []

# main.py
from routes.users import users_bp
app.register_blueprint(users_bp)
```

## Practice exercises
1. Build a `/calculate/<op>/<a>/<b>` endpoint supporting `add`, `sub`, `mul`, `div`.
2. Create an HTML form (`templates/form.html`) that POSTs to `/submit` and displays the submitted value.
3. Add a `Book` in-memory list and CRUD routes (`GET/POST/PUT/DELETE /books/<id>`).
4. Use a Blueprint to separate `books` routes from `main.py`.
