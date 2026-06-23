"""Database creation and schema initialization utility."""

import logging
import os
import re

import mysql.connector

from App.config import DB_CONFIG

logger = logging.getLogger(__name__)

DB_USER = DB_CONFIG["user"]
DB_PASS = DB_CONFIG["password"]
DB_HOST = DB_CONFIG["host"]
DB_NAME = DB_CONFIG["database"]
DB_PORT = DB_CONFIG["port"]
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SQL_FILE_PATH = os.path.join(BASE_DIR, "SQL", "database.sql")


def _exec_statements(cursor: "mysql.connector.cursor.MySQLCursor", sql_text: str) -> None:
    """Remove comments and execute each statement in *sql_text*."""
    sql_clean = re.sub(r"--.*\n", "\n", sql_text)
    sql_clean = re.sub(r"/\*.*?\*/", "", sql_clean, flags=re.S)
    commands = [c.strip() for c in sql_clean.split(";") if c.strip()]
    for cmd in commands:
        cursor.execute(cmd)


def setup_nuclear() -> None:
    """Drop and recreate the database, then run the full DDL script."""

    # connect as root (no database) to drop/create the database
    try:
        conn_root = mysql.connector.connect(
            host=DB_HOST, user=DB_USER, password=DB_PASS, port=DB_PORT
        )
        conn_root.autocommit = True
        cur = conn_root.cursor()
        try:
            cur.execute(f"DROP DATABASE IF EXISTS `{DB_NAME}`")
            logger.info("Dropped existing database '%s'.", DB_NAME)
            cur.execute(
                f"CREATE DATABASE `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
            logger.info("Created database '%s'.", DB_NAME)
        finally:
            cur.close()
    except Exception as e:
        logger.error("Root connection failed: %s", e)
        return
    finally:
        try:
            conn_root.close()
        except Exception:
            pass

    # connect to the newly created database and run SQL script
    try:
        with open(SQL_FILE_PATH, "r", encoding="utf-8") as f:
            sql_script = f.read()
    except FileNotFoundError:
        logger.error("SQL file not found: '%s'.", SQL_FILE_PATH)
        return

    try:
        conn_db = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS,
            port=DB_PORT,
            database=DB_NAME,
        )
        conn_db.autocommit = True
        cur = conn_db.cursor()
        try:
            cur.execute("SET FOREIGN_KEY_CHECKS = 0;")
            _exec_statements(cur, sql_script)
            cur.execute("SET FOREIGN_KEY_CHECKS = 1;")
            logger.info("Database schema applied successfully.")
        finally:
            cur.close()
    except Exception as e:
        logger.error("Unexpected error during schema setup: %s", e)
    finally:
        try:
            conn_db.close()
        except Exception:
            pass


if __name__ == "__main__":
    setup_nuclear()
