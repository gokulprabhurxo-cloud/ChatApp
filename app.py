from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_socketio import SocketIO, emit
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = "gokul123"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///chat.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# eventlet is simplest for free-tier hosts that support websockets
socketio = SocketIO(app, async_mode="threading")

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

with app.app_context():
    db.create_all()

@app.get("/")
def index():
    return redirect(url_for("chat")) if current_user.is_authenticated else redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if not username or not password:
            flash("Username and password required.")
            return redirect(url_for("register"))

        if User.query.filter_by(username=username).first():
            flash("Username already taken.")
            return redirect(url_for("register"))

        user = User(username=username, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        flash("Registration successful. Please log in.")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter_by(username=username).first()

        if not user or not check_password_hash(user.password_hash, password):
            flash("Invalid username or password.")
            return redirect(url_for("login"))

        login_user(user)
        return redirect(url_for("chat"))

    return render_template("login.html")

@app.get("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.get("/chat")
@login_required
def chat():
    return render_template("chat.html", username=current_user.username)

# ---- Realtime events ----
@socketio.on("send_message")
def handle_send_message(data):
    # Only allow logged-in users to send
    if not current_user.is_authenticated:
        return

    text = (data or {}).get("text", "").strip()
    if not text:
        return

    payload = {
        "username": current_user.username,
        "text": text,
        "ts": datetime.utcnow().strftime("%H:%M:%S UTC"),
    }
    emit("new_message", payload, broadcast=True)

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port)