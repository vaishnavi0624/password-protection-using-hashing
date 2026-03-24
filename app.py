from flask import Flask, render_template, request, redirect, flash, session
import hashlib, json, os

app = Flask(__name__)
app.secret_key = "secret123"

DATA_FILE = "users.json"

def load_users():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(DATA_FILE, "w") as f:
        json.dump(users, f)

# 🔐 Salted hashing
def hash_password(password):
    salt = os.urandom(16).hex()
    hash_val = hashlib.sha256((password + salt).encode()).hexdigest()
    return salt + ":" + hash_val

def verify_password(stored, password):
    salt, hash_val = stored.split(":")
    return hashlib.sha256((password + salt).encode()).hexdigest() == hash_val

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        users = load_users()

        if username in users:
            flash("User already exists ❌")
            return redirect("/register")

        users[username] = hash_password(password)
        save_users(users)

        flash("Registration Successful ✅")
        return redirect("/login")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        users = load_users()

        if username not in users:
            flash("User not found ❌")
            return redirect("/login")

        if verify_password(users[username], password):
            session["user"] = username
            return redirect("/dashboard")
        else:
            flash("Incorrect Password ❌")
            return redirect("/login")

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user" in session:
        return render_template("dashboard.html", user=session["user"])
    return redirect("/login")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)