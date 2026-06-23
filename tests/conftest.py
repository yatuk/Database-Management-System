"""pytest fixtures for the WDI Flask application."""

import os
import secrets

import pytest

# Set required env vars before any app imports
os.environ.setdefault("DB_PASSWORD", "test_pass")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing-only")
os.environ.setdefault("FLASK_DEBUG", "0")
os.environ.setdefault("SESSION_COOKIE_SECURE", "0")


@pytest.fixture
def app():
    """Create a Flask app instance for testing."""
    from App.routes import create_app

    application = create_app()
    application.config.update(
        {
            "TESTING": True,
            "SECRET_KEY": "test-key",
        }
    )
    return application


@pytest.fixture
def client(app):
    """Flask test client."""
    return app.test_client()


@pytest.fixture
def csrf_token(client):
    """Generate a valid CSRF token and inject it into the session."""
    token = secrets.token_hex(32)
    with client.session_transaction() as sess:
        sess["csrf_token"] = token
    return token


@pytest.fixture
def admin_session(client):
    """Simulate an admin login session."""
    with client.session_transaction() as sess:
        sess["student_id"] = 1
        sess["student_number"] = "820230326"
        sess["team_no"] = 1


@pytest.fixture
def editor_session(client):
    """Simulate an editor login session."""
    with client.session_transaction() as sess:
        sess["student_id"] = 6
        sess["student_number"] = "5454"
        sess["team_no"] = 2
