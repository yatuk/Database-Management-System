"""Seed admin and editor user accounts."""

import logging
import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from App.routes import create_app  # type: ignore
from App.db import get_db

logger = logging.getLogger(__name__)


def seed_students() -> None:
    """
    Seed admin and editor users into the students table.

    Admins: team_no = 1
    Editor: student_number = 5454, team_no = 2
    """
    db = get_db()
    cur = db.cursor()

    sql = """
        INSERT INTO students (student_number, full_name, team_no)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE
          full_name = VALUES(full_name),
          team_no   = VALUES(team_no)
    """

    rows = [
        # Admin users (team_no = 1)
        ("820230313", "Salih Sefer", 1),
        ("820230334", "Atahan Evintan", 1),
        ("820230326", "Fatih Serdar Cakmak", 1),
        ("820230314", "Muhammet Tuncer", 1),
        ("150210085", "Gulbahar Karabas", 1),
        # Editor user (team_no = 2)
        ("5454", "Editor User", 2),
    ]

    for sn, name, team in rows:
        cur.execute(sql, (sn, name, team))

    db.commit()
    cur.close()
    logger.info("Successfully seeded %d student accounts.", len(rows))


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        seed_students()
