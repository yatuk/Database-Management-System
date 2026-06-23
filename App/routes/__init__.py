import os
import secrets
from datetime import timedelta

from flask import (
    Flask,
    redirect,
    url_for,
    session,
    request,
    abort,
    g,
)
from App.db import close_db
from App.config import (
    SECRET_KEY,
    DEBUG,
    SESSION_COOKIE_SECURE,
    SESSION_COOKIE_HTTPONLY,
    SESSION_COOKIE_SAMESITE,
    PERMANENT_SESSION_LIFETIME,
)

# Project base directory (root of the repo)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def create_app() -> Flask:
    """Create and configure the Flask application."""

    app = Flask(
        __name__,
        template_folder=os.path.join(BASE_DIR, "frontend", "css", "templates"),
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
        """Validate CSRF token on all state-changing requests."""
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return

        # Generate a CSRF token on first access and store it in the session.
        if "csrf_token" not in session:
            session["csrf_token"] = secrets.token_hex(32)

        token = request.form.get("csrf_token") or request.headers.get(
            "X-CSRF-Token"
        )
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
        response.headers[
            "Content-Security-Policy"
        ] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.googleapis.com; "
            "font-src 'self' https://cdnjs.cloudflare.com https://fonts.gstatic.com; "
            "img-src 'self' data:; "
            "connect-src 'self'"
        )
        return response

    # ---- Blueprints ----
    from App.routes.sustainability import sustainability_bp
    from App.routes.about import about_bp
    from App.routes.login import login_bp, get_current_role
    from App.routes.health import health_bp
    from App.routes.dashboard import dashboard_bp
    from App.routes.freshwater import freshwater_bp
    from App.routes.ghg import ghg_bp
    from App.routes.energy import energy_bp
    from App.routes.countries import countries_bp

    app.register_blueprint(countries_bp)
    app.register_blueprint(about_bp)
    app.register_blueprint(login_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(sustainability_bp)
    app.register_blueprint(freshwater_bp)
    app.register_blueprint(ghg_bp)
    app.register_blueprint(energy_bp)

    # ---- Global Template Context ----
    @app.context_processor
    def inject_role_and_csrf():
        """Expose current user role and CSRF token to all templates."""
        role = get_current_role()
        return {
            "current_role": role,
            "is_admin": role == "admin",
            "is_editor": role == "editor",
            "is_viewer": role == "viewer",
            "csrf_token": session.get("csrf_token", ""),
        }

    # ---- Root redirect ----
    @app.route("/")
    def index():
        return redirect(url_for("auth.login"))

    return app
