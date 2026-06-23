"""Tests for authentication and authorization (JSON API)."""

from unittest.mock import MagicMock, patch


class TestLoginFlow:
    """Login endpoint tests."""

    def test_login_requires_csrf(self, client):
        """POST without CSRF token should return 400."""
        response = client.post(
            "/auth/login",
            data={"student_number": "test", "password": "x"},
        )
        assert response.status_code == 400
        assert b"CSRF" in response.data

    def test_login_empty_student_number(self, client, csrf_token):
        """Empty student number should return 400."""
        response = client.post(
            "/auth/login",
            data={"student_number": "", "password": "", "csrf_token": csrf_token},
        )
        assert response.status_code == 400

    @patch("App.routes.login.get_db")
    def test_login_valid_admin(self, mock_get_db, client, csrf_token):
        """Valid admin login returns success JSON."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {
            "student_id": 1,
            "student_number": "820230326",
            "full_name": "Test Admin",
            "team_no": 1,
            "password_hash": None,
        }
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db.return_value = mock_conn

        response = client.post(
            "/auth/login",
            data={
                "student_number": "820230326",
                "password": "",
                "csrf_token": csrf_token,
            },
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["user"]["role"] == "admin"

    @patch("App.routes.login.get_db")
    def test_login_nonexistent_user(self, mock_get_db, client, csrf_token):
        """Non-existent user returns 401."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db.return_value = mock_conn

        response = client.post(
            "/auth/login",
            data={
                "student_number": "999999",
                "password": "",
                "csrf_token": csrf_token,
            },
        )
        assert response.status_code == 401
        assert response.get_json()["error"] == "User not found."

    @patch("App.routes.login.get_db")
    def test_login_viewer_rejected(self, mock_get_db, client, csrf_token):
        """Viewer-level user should get 403."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {
            "student_id": 99,
            "student_number": "000000",
            "full_name": "Viewer",
            "team_no": 0,
            "password_hash": None,
        }
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db.return_value = mock_conn

        response = client.post(
            "/auth/login",
            data={
                "student_number": "000000",
                "password": "",
                "csrf_token": csrf_token,
            },
        )
        assert response.status_code == 403


class TestLogout:
    """Logout tests."""

    def test_logout_returns_200(self, client):
        """Logout returns JSON success."""
        response = client.get("/auth/logout")
        assert response.status_code == 200
        assert response.get_json()["success"] is True

    def test_logout_clears_session(self, client, admin_session):
        """Logout clears the session."""
        client.get("/auth/logout")
        with client.session_transaction() as sess:
            assert "student_id" not in sess


class TestRoleHelpers:
    """Test RBAC decorators on protected endpoints."""

    def test_editor_cannot_access_delete(self, client, editor_session, csrf_token):
        """Editor gets 403 when trying to delete."""
        response = client.post(
            "/api/energy/delete/1",
            headers={"X-CSRF-Token": csrf_token},
        )
        assert response.status_code == 403


class TestAuthMe:
    """/api/auth/me endpoint tests."""

    def test_auth_me_unauthenticated(self, client):
        """Unauthenticated user gets viewer role."""
        response = client.get("/api/auth/me")
        assert response.status_code == 200
        data = response.get_json()
        assert data["authenticated"] is False
        assert data["role"] == "viewer"

    def test_auth_me_admin(self, client, admin_session):
        """Admin session shows admin role."""
        response = client.get("/api/auth/me")
        assert response.status_code == 200
        data = response.get_json()
        assert data["authenticated"] is True
        assert data["role"] == "admin"
