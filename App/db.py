"""Database connection utilities -- request-scoped MySQL connections."""

import mysql.connector
from flask import g

from App.config import DB_CONFIG


def get_db():
    """
    Return a single MySQL connection for the current Flask request context.

    The connection is cached in ``flask.g`` so that multiple calls within
    the same request reuse the same underlying connection.
    """
    if "db" not in g:
        g.db = mysql.connector.connect(**DB_CONFIG)
    return g.db


def close_db(e: object = None) -> None:
    """
    Close the MySQL connection at the end of the request, if one exists.

    Registered with ``app.teardown_appcontext`` so Flask calls it
    automatically after every request.
    """
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()
