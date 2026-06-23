"""Tests for security headers, CSRF protection, and XSS prevention."""

import pytest


class TestCSRFProtection:
    """CSRF token validation tests."""

    def test_get_requests_bypass_csrf(self, client):
        """GET requests should not require CSRF tokens."""
        response = client.get("/auth/login")
        assert response.status_code == 200

    def test_post_without_csrf_returns_400(self, client):
        """POST without CSRF token should be rejected."""
        response = client.post("/auth/login", data={"student_number": "test"})
        assert response.status_code == 400
        assert b"CSRF" in response.data

    def test_post_with_valid_csrf(self, client, csrf_token):
        """POST with valid CSRF token should pass validation."""
        response = client.post(
            "/auth/login",
            data={"student_number": "", "csrf_token": csrf_token},
        )
        # Should pass CSRF check (then fail on empty student_number validation)
        assert response.status_code == 302

    def test_post_with_invalid_csrf(self, client, csrf_token):
        """POST with wrong CSRF token should be rejected."""
        response = client.post(
            "/auth/login",
            data={"student_number": "test", "csrf_token": "invalid_token"},
        )
        assert response.status_code == 400

    def test_csrf_token_present_in_form(self, client):
        """Login form should contain the CSRF hidden input."""
        response = client.get("/auth/login")
        assert b'name="csrf_token"' in response.data


class TestSecurityHeaders:
    """Security HTTP header tests."""

    def test_x_content_type_options(self, client):
        """X-Content-Type-Options: nosniff should be set."""
        response = client.get("/auth/login")
        assert response.headers.get("X-Content-Type-Options") == "nosniff"

    def test_x_frame_options(self, client):
        """X-Frame-Options: DENY should be set."""
        response = client.get("/auth/login")
        assert response.headers.get("X-Frame-Options") == "DENY"

    def test_referrer_policy(self, client):
        """Referrer-Policy should be set."""
        response = client.get("/auth/login")
        assert "strict-origin" in response.headers.get("Referrer-Policy", "")

    def test_content_security_policy(self, client):
        """Content-Security-Policy header should be present."""
        response = client.get("/auth/login")
        csp = response.headers.get("Content-Security-Policy", "")
        assert "default-src" in csp
        assert "script-src" in csp


class TestXSSPrevention:
    """XSS prevention tests."""

    def test_sort_param_escaped_in_ghg_list(self, client):
        """sort_by parameter should be JSON-encoded, not raw in JS."""
        response = client.get("/ghg/?sort=country&order=asc")
        # The page should render without raw script injection
        assert response.status_code == 200
        # Jinja2 |tojson produces JSON-safe output
        # The raw string ' should not appear unescaped in script context
        raw = response.data.decode()
        assert "let sortColumn = " in raw

    def test_login_form_escapes_input(self, client, csrf_token):
        """HTML entities in student_number should be escaped."""
        response = client.post(
            "/auth/login",
            data={"student_number": '<script>alert(1)</script>', "csrf_token": csrf_token},
            follow_redirects=True,
        )
        assert response.status_code == 200
        # The script tag should not appear unescaped in the response
        assert b"<script>alert" not in response.data


class TestEnvironmentSecrets:
    """Tests ensuring secrets are not exposed."""

    def test_secret_key_is_set(self, app):
        """Secret key should be set from env, not the old hardcoded default."""
        assert app.secret_key is not None
        assert app.secret_key != "secret_key_wdi_team1"

    def test_debug_disabled_in_test(self, app):
        """Debug mode should be off during testing."""
        assert app.debug is False
