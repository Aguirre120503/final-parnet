# app/auth.py
from functools import wraps

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user,
)
from werkzeug.security import check_password_hash

from .models import Usuario

# Blueprint correctamente definido
auth_bp = Blueprint("auth", __name__)


# --------- DECORADOR admin_required ----------
def admin_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapped_view(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash("No tienes permisos de administrador.", "danger")
            return redirect(url_for("public.index"))
        return view_func(*args, **kwargs)

    return wrapped_view


# --------- LOGIN ----------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        # TU INPUT SE LLAMA "email", LO ACEPTAMOS COMO USERNAME O CORREO
        login_id = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        # Buscar por username O por email
        user = Usuario.query.filter(
            (Usuario.username == login_id) | (Usuario.email == login_id)
        ).first()

        if not user or not check_password_hash(user.password_hash, password):
            flash("Usuario o contraseña incorrectos", "danger")
            return render_template("login.html")

        login_user(user)
        flash(f"Bienvenido, {user.username}.", "success")
        return redirect(url_for("admin.dashboard"))

    return render_template("login.html")


# --------- LOGOUT ----------
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada correctamente.", "info")
    return redirect(url_for("public.index"))