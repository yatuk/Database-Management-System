"""Tests for authentication and authorization."""

from unittest.mock import MagicMock, patch

import pytest


class TestLoginFlow:
    """Login page and authentication tests."""

    def test_login_page_renders(self, client):
        """Login page should return 200 with the login form."""
        response = client.get("/auth/login")
        assert response.status_code == 200
        assert b"Student Number" in response.data

    def test_login_empty_student_number(self, client, csrf_token):
        """Empty student number should redirect back to login with flash."""
        response = client.post(
            "/auth/login",
            data={"student_number": "", "csrf_token": csrf_token},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Student Number" in response.data

    @patch("App.routes.login.get_db")
    def test_login_valid_admin(self, mock_get_db, client, csrf_token):
        """Valid admin student number should redirect to dashboard."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {
            "student_id": 1,
            "student_number": "820230326",
            "full_name": "Test Admin",
            "team_no": 1,
        }
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db.return_value = mock_conn

        response = client.post(
            "/auth/login",
            data={"student_number": "820230326", "csrf_token": csrf_token},
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert "/dashboard" in response.headers["Location"]

    @patch("App.routes.login.get_db")
    def test_login_nonexistent_user(self, mock_get_db, client, csrf_token):
        """Non-existent student number should redirect back to login."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db.return_value = mock_conn

        response = client.post(
            "/auth/login",
            data={"student_number": "999999", "csrf_token": csrf_token},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"User not found" in response.data

    @patch("App.routes.login.get_db")
    def test_login_viewer_rejected(self, mock_get_db, client, csrf_token):
        """Viewer-level user (team_no=0) should be rejected."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {
            "student_id": 99,
            "student_number": "000000",
            "full_name": "Viewer",
            "team_no": 0,
        }
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db.return_value = mock_conn

        response = client.post(
            "/auth/login",
            data={"student_number": "000000", "csrf_token": csrf_token},
            follow_redirects=True,
        )
        assert b"do not have permission" in response.data


class TestLogout:
    """Logout tests."""

    def test_logout_clears_session(self, client, admin_session):
        """Logout should clear the session and redirect to login."""
        response = client.get("/auth/logout", follow_redirects=False)
        assert response.status_code == 302
        assert "/auth/login" in response.headers["Location"]

        with client.session_transaction() as sess:
            assert "student_id" not in sess


class TestRoleHelpers:
    """Test RBAC decorators on protected endpoints."""

    def test_editor_cannot_access_delete(self, client, editor_session, csrf_token):
        """Editor should get 403 when trying to delete."""
        response = client.post(
            "/ghg/api/delete/1",
            json={"csrf_token": csrf_token},
            headers={"X-CSRF-Token": csrf_token},
            content_type="application/json",
        )
        assert response.status_code == 403
