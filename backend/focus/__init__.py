import os

from flask import Flask, jsonify, request, send_from_directory
from werkzeug.exceptions import HTTPException

from focus.config import Config
from focus.extensions import cors, db, jwt

API_PREFIX = "/api/v1"


def create_app(config_object: type[Config] = Config) -> Flask:
    static_dir = os.environ.get(
        "FOCUS_STATIC_DIR", os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
    )
    app = Flask(__name__, static_folder=static_dir, static_url_path="")
    app.config.from_object(config_object)

    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}})

    _register_jwt_hooks()
    _register_blueprints(app)
    _register_error_handlers(app)
    _register_spa(app)

    with app.app_context():
        db.create_all()
        from focus.services.gamification import seed_achievements

        seed_achievements()

    return app


def _register_blueprints(app: Flask) -> None:
    from focus.api import (
        auth_bp,
        blocked_apps_bp,
        challenges_bp,
        sessions_bp,
        stats_bp,
        users_bp,
    )

    app.register_blueprint(auth_bp, url_prefix=f"{API_PREFIX}/auth")
    app.register_blueprint(users_bp, url_prefix=f"{API_PREFIX}/users")
    app.register_blueprint(sessions_bp, url_prefix=f"{API_PREFIX}/sessions")
    app.register_blueprint(stats_bp, url_prefix=f"{API_PREFIX}/stats")
    app.register_blueprint(challenges_bp, url_prefix=f"{API_PREFIX}/challenges")
    app.register_blueprint(blocked_apps_bp, url_prefix=f"{API_PREFIX}/blocked-apps")

    @app.get(f"{API_PREFIX}/health")
    def health():
        return jsonify({"status": "ok", "service": "focus-api", "version": "2.0.0"})


def _register_jwt_hooks() -> None:
    from focus.models import RevokedToken

    @jwt.token_in_blocklist_loader
    def is_revoked(_jwt_header, jwt_payload) -> bool:
        return db.session.query(
            RevokedToken.query.filter_by(jti=jwt_payload["jti"]).exists()
        ).scalar()

    @jwt.unauthorized_loader
    def missing_token(reason):
        return jsonify({"error": "Falta el token de acceso", "detail": reason}), 401

    @jwt.invalid_token_loader
    def invalid_token(reason):
        return jsonify({"error": "Token inválido", "detail": reason}), 422

    @jwt.expired_token_loader
    def expired_token(_header, _payload):
        return jsonify({"error": "Token expirado"}), 401

    @jwt.revoked_token_loader
    def revoked_token(_header, _payload):
        return jsonify({"error": "Token revocado"}), 401


def _register_error_handlers(app: Flask) -> None:
    @app.errorhandler(HTTPException)
    def handle_http_exception(exc: HTTPException):
        if request.path.startswith("/api/"):
            return jsonify({"error": exc.description}), exc.code
        return exc

    @app.errorhandler(Exception)
    def handle_unexpected(exc: Exception):
        app.logger.exception("Error no controlado", exc_info=exc)
        db.session.rollback()
        return jsonify({"error": "Error interno del servidor"}), 500


def _register_spa(app: Flask) -> None:
    """Sirve la web app construida (si existe) para rutas no-API."""

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def spa(path: str):
        static_dir = app.static_folder
        if static_dir is None:
            return jsonify({"error": "Web app no construida"}), 404
        target = os.path.join(static_dir, path)
        if path and os.path.isfile(target):
            return send_from_directory(static_dir, path)
        index = os.path.join(static_dir, "index.html")
        if os.path.isfile(index):
            return send_from_directory(static_dir, "index.html")
        return jsonify({"error": "Web app no construida", "api": f"{API_PREFIX}/health"}), 404
