from flask import abort
from flask_jwt_extended import get_jwt_identity

from focus.extensions import db
from focus.models import User


def current_user() -> User:
    user = db.session.get(User, int(get_jwt_identity()))
    if user is None:
        abort(404, description="Usuario no encontrado")
    return user
