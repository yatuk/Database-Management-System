"""Authentication blueprint -- JSON API for React SPA."""

from functools import wraps
from typing import Callable

from flask import (
    Blueprint,
    abort,
    jsonify,
    request,
    session,
)
from werkzeug.security import check_password_hash

from App.db import get_db

login_bp = Blueprint("auth", __name__, url_prefix="/auth")


# ---- Role helpers ----

def get_current_role() -> str:
    team = session.get("team_no", 0)
    try:
        team = int(team)
    except (TypeError, ValueError):
        team = 0
    if team == 1:
        return "admin"
    if team == 2:
        return "editor"
    return "viewer"


def editor_required(f: Callable) -> Callable:
    @wraps(f)
    def decorated_function(*args: object, **kwargs: object) -> object:
        if get_current_role() not in ("editor", "admin"):
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f: Callable) -> Callable:
    @wraps(f)
    def decorated_function(*args: object, **kwargs: object) -> object:
        if get_current_role() != "admin":
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


# ---- Login ----

@login_bp.route("/login", methods=["POST"])
def login():
    """Authenticate and return JSON."""
    entered_number = request.form.get("student_number", "").strip()
    entered_password = request.form.get("password", "").strip()

    if not entered_number:
        return jsonify({"success": False, "error": "Please enter a student number."}), 400

    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        """
        SELECT student_id, student_number, full_name, team_no, password_hash
        FROM students WHERE student_number = %s
        """,
        (entered_number,),
    )
    student = cur.fetchone()
    cur.close()

    if not student:
        return jsonify({"success": False, "error": "User not found."}), 401

    team_no = int(student.get("team_no") or 0)
    if team_no not in (1, 2):
        return jsonify({"success": False, "error": "You do not have permission."}), 403

    password_hash = student.get("password_hash")
    if password_hash:
        if not entered_password:
            return jsonify({"success": False, "error": "Please enter your password."}), 400
        if not check_password_hash(password_hash, entered_password):
            return jsonify({"success": False, "error": "Invalid password."}), 401

    session["student_id"] = student["student_id"]
    session["student_number"] = student["student_number"]
    session["team_no"] = team_no

    return jsonify({
        "success": True,
        "user": {
            "student_id": student["student_id"],
            "student_number": student["student_number"],
            "full_name": student["full_name"],
            "role": get_current_role(),
        },
    })


# ---- Logout ----

@login_bp.route("/logout")
def logout():
    session.clear()
    return jsonify({"success": True})
