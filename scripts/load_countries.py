"""Load country data from CSV into the database."""

import csv
import logging
import os
import sys

import mysql.connector

# ensure repository root is on sys.path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from App.config import DB_CONFIG  # noqa: E402

logger = logging.getLogger(__name__)

DB_USER = DB_CONFIG["user"]
DB_PASS = DB_CONFIG["password"]
DB_HOST = DB_CONFIG["host"]
DB_PORT = DB_CONFIG["port"]
DB_NAME = DB_CONFIG["database"]

CSV_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "Data",
    "countries.csv",
)


def load() -> None:
    """Read countries.csv and insert into the countries table."""
    rows = []
    with open(CSV_PATH, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for r in reader:
            cid = int(r.get("country_id", 0) or 0)
            name = (r.get("country_name") or "").strip()
            code = (r.get("country_code") or "").strip()
            region = (r.get("region") or "").strip()
            rows.append((cid, name, code, region))

    if not rows:
        logger.warning("No countries found in %s", CSV_PATH)
        return

    conn = mysql.connector.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASS, database=DB_NAME, port=DB_PORT
    )
    try:
        with conn.cursor() as cur:
            cur.execute("SET FOREIGN_KEY_CHECKS=0;")
            cur.execute("TRUNCATE TABLE countries;")
            insert_sql = (
                "INSERT INTO countries (country_id, country_name, country_code, region) "
                "VALUES (%s, %s, %s, %s)"
            )
            cur.executemany(insert_sql, rows)
            cur.execute("SET FOREIGN_KEY_CHECKS=1;")
        conn.commit()
    finally:
        conn.close()

    logger.info("Loaded %d countries from %s", len(rows), CSV_PATH)


if __name__ == "__main__":
    load()
