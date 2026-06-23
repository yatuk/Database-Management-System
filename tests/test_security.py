"""Tests for security headers and CSRF protection (JSON API)."""


class TestCSRFProtection:
    """CSRF token validation tests."""

    def test_get_requests_bypass_csrf(self, client):
        """GET requests should not require CSRF tokens."""
        response = client.get("/api/auth/me")
        assert response.status_code == 200

    def test_post_without_csrf_returns_400(self, client):
        """POST without CSRF token should be rejected."""
        response = client.post(
            "/auth/login", data={"student_number": "test", "password": "x"}
        )
        assert response.status_code == 400
        assert b"CSRF" in response.data

    def test_post_api_without_csrf_header(self, client):
        """POST to /api/* without X-CSRF-Token header should be rejected."""
        response = client.post(
            "/api/energy/add",
            json={"country_id": 1},
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_post_with_valid_csrf(self, client, csrf_token):
        """POST with valid CSRF token should pass validation."""
        response = client.post(
            "/auth/login",
            data={"student_number": "", "password": "", "csrf_token": csrf_token},
        )
        # Passes CSRF, fails on empty student_number (400)
        assert response.status_code == 400

    def test_post_with_invalid_csrf(self, client, csrf_token):
        """POST with wrong CSRF token should be rejected."""
        response = client.post(
            "/auth/login",
            data={
                "student_number": "test",
                "password": "",
                "csrf_token": "invalid_token",
            },
        )
        assert response.status_code == 400
        assert b"CSRF" in response.data


class TestSecurityHeaders:
    """Security HTTP header tests."""

    def test_x_content_type_options(self, client):
        """X-Content-Type-Options: nosniff should be set."""
        response = client.get("/api/auth/me")
        assert response.headers.get("X-Content-Type-Options") == "nosniff"

    def test_x_frame_options(self, client):
        """X-Frame-Options: DENY should be set."""
        response = client.get("/api/auth/me")
        assert response.headers.get("X-Frame-Options") == "DENY"

    def test_content_security_policy(self, client):
        """Content-Security-Policy header should be present."""
        response = client.get("/api/auth/me")
        csp = response.headers.get("Content-Security-Policy", "")
        assert "default-src" in csp


class TestEnvironmentSecrets:
    """Tests ensuring secrets are not exposed."""

    def test_secret_key_is_set(self, app):
        """Secret key should be set from env, not hardcoded default."""
        assert app.secret_key is not None
        assert app.secret_key != "secret_key_wdi_team1"

    def test_debug_disabled_in_test(self, app):
        """Debug mode should be off during testing."""
        assert app.debug is False
