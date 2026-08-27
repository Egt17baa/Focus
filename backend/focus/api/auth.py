import re

from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
)

from focus.extensions import db
from focus.models import RevokedToken, User

auth_bp = Blueprint("auth", __name__)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
USERNAME_RE = re.compile(r"^[a-zA-Z0-9_.-]{3,30}$")


def validate_credentials(username: str, email: str, password: str) -> str | None:
    if not USERNAME_RE.match(username or ""):
        return "El usuario debe tener 3-30 caracteres alfanuméricos"
    if not EMAIL_RE.match(email or ""):
        return "Email inválido"
    if len(password or "") < 8:
        return "La contraseña debe tener al menos 8 caracteres"
    return None


def tokens_for(user: User) -> dict:
    identity = str(user.id)
    return {
        "access_token": create_access_token(identity=identity),
        "refresh_token": create_refresh_token(identity=identity),
        "user": user.to_dict(),
    }


@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    error = validate_credentials(username, email, password)
    if error:
        return jsonify({"error": error}), 400
    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({"error": "El usuario o email ya está registrado"}), 409

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify(tokens_for(user)), 201


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    identifier = (data.get("username") or data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    user = User.query.filter(
        (db.func.lower(User.username) == identifier) | (User.email == identifier)
    ).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Credenciales inválidas"}), 401
    return jsonify(tokens_for(user)), 200


@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    user = db.session.get(User, int(get_jwt_identity()))
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404
    return jsonify({"access_token": create_access_token(identity=str(user.id))}), 200


@auth_bp.post("/logout")
@jwt_required(verify_type=False)
def logout():
    db.session.add(RevokedToken(jti=get_jwt()["jti"]))
    db.session.commit()
    return jsonify({"message": "Sesión cerrada"}), 200


@auth_bp.post("/change-password")
@jwt_required()
def change_password():
    data = request.get_json(silent=True) or {}
    user = db.session.get(User, int(get_jwt_identity()))
    if not user or not user.check_password(data.get("current_password") or ""):
        return jsonify({"error": "Contraseña actual incorrecta"}), 401
    new_password = data.get("new_password") or ""
    if len(new_password) < 8:
        return jsonify({"error": "La nueva contraseña debe tener al menos 8 caracteres"}), 400
    user.set_password(new_password)
    db.session.commit()
    return jsonify({"message": "Contraseña actualizada"}), 200
