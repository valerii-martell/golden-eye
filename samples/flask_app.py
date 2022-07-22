from flask import Flask


app = Flask(__name__)


@app.route("/hello")
def hello():
    return "Hello world!"


@app.route("/hello/<name>")
def hello_name(name):
    return f"Hello {name}!"


@app.route("/user/<int:user_id>")
@app.route("/user/<float:user_id>")
def hello_user_id(user_id):
    return f"Hello user {user_id}!"


@app.route("/height/<float:height>")
def hello_height(height):
    return f"Hello user with height {height}!"


@app.route("/path/<path:subpath>")
def show_subpath(subpath):
    return f"Subpath: {subpath}"


app.run(debug=True)
