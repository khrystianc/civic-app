"""
Basic email/password auth. Kept intentionally simple - no email
verification or password reset flow yet, both worth adding before
a real public launch (see README TODOs).
"""
from flask import Blueprint, request, jsonify, redirect, url_for, render_template
from flask_login import login_user, logout_user, login_required, current_user

from app.models import db, User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    if not email or not password:
        return render_template("signup.html", error="Email and password are required.")

    if User.query.filter_by(email=email).first():
        return render_template("signup.html", error="An account with that email already exists.")

    user = User(email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    login_user(user)
    return redirect(url_for("pages.index"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return render_template("login.html", error="Invalid email or password.")

    login_user(user)
    return redirect(url_for("pages.index"))


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("pages.index"))


@auth_bp.route("/api/me")
def me():
    if not current_user.is_authenticated:
        return jsonify({"authenticated": False})
    return jsonify({
        "authenticated": True,
        "email": current_user.email,
        "subscribed": current_user.is_subscribed,
    })
