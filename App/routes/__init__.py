"""Flask application factory -- React SPA + REST API backend."""

import os
import secrets
from datetime import timedelta

from flask import (
    Flask,
    abort,
    redirect,
    request,
    send_from_directory,
    session,
    url_for,
)

from App.config import (
    PERMANENT_SESSION_LIFETIME,
    SECRET_KEY,
    SESSION_COOKIE_HTTPONLY,
    SESSION_COOKIE_SAMESITE,
    SESSION_COOKIE_SECURE,
)
from App.db import close_db

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
REACT_DIST = os.path.join(BASE_DIR, "react", "dist")


def create_app() -> Flask:
    """Create and configure the Flask application."""

    app = Flask(
        __name__,
        static_folder=os.path.join(BASE_DIR, "frontend", "css"),
    )

    # ---- Secret Key ----
    if not SECRET_KEY:
        raise RuntimeError(
            "Missing required environment variable: SECRET_KEY. "
            "Copy .env.example to .env and fill in the values."
        )
    app.secret_key = SECRET_KEY

    # ---- Session Security ----
    app.config["SESSION_COOKIE_SECURE"] = SESSION_COOKIE_SECURE
    app.config["SESSION_COOKIE_HTTPONLY"] = SESSION_COOKIE_HTTPONLY
    app.config["SESSION_COOKIE_SAMESITE"] = SESSION_COOKIE_SAMESITE
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(
        seconds=PERMANENT_SESSION_LIFETIME
    )

    # ---- Teardown ----
    app.teardown_appcontext(close_db)

    # ---- Rate Limiting ----
    try:
        from flask_limiter import Limiter
        from flask_limiter.util import get_remote_address

        Limiter(
            app=app,
            key_func=get_remote_address,
            default_limits=["200 per day", "50 per hour"],
            storage_uri="memory://",
        )
    except ImportError:
        pass

    # ---- CSRF Protection ----
    @app.before_request
    def csrf_protect():
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return
        if "csrf_token" not in session:
            session["csrf_token"] = secrets.token_hex(32)
        if request.path.startswith("/api/"):
            token = request.headers.get("X-CSRF-Token")
        else:
            token = request.form.get("csrf_token")
        if not token or not secrets.compare_digest(
            token, session.get("csrf_token", "")
        ):
            abort(400, description="CSRF token missing or invalid.")

    # ---- Security Headers ----
    @app.after_request
    def set_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.googleapis.com; "
            "font-src 'self' https://cdnjs.cloudflare.com https://fonts.gstatic.com; "
            "img-src 'self' data:; "
            "connect-src 'self'"
        )
        return response

    # ---- Blueprints ----
    from App.routes.api import api_bp  # /api/*  (all JSON endpoints)
    from App.routes.login import login_bp  # /auth/login, /auth/logout

    app.register_blueprint(api_bp)
    app.register_blueprint(login_bp)

    # ---- React SPA routes ----
    react_ready = os.path.isdir(REACT_DIST)

    @app.route("/")
    def index():
        if react_ready:
            return send_from_directory(REACT_DIST, "index.html")
        return redirect(url_for("auth.login"))

    if react_ready:
        @app.route("/assets/<path:filename>")
        def react_assets(filename: str):
            return send_from_directory(os.path.join(REACT_DIST, "assets"), filename)

        @app.route("/<path:path>")
        def spa_fallback(path: str):
            reserved = ("api", "auth")
            if path.split("/")[0] in reserved:
                abort(404)
            ext = os.path.splitext(path)[1]
            if ext and ext not in (".html", ""):
                try:
                    return send_from_directory(REACT_DIST, path)
                except Exception:
                    abort(404)
            return send_from_directory(REACT_DIST, "index.html")

    return app
