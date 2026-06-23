"""Base class for domain CRUD blueprints.

Each domain (energy, freshwater, ghg, health, sustainability) can subclass
``DomainCRUD`` and override the class-level config attributes. This eliminates
~2000 lines of duplicated CRUD logic across the 5 route files.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from App.db import get_db
from App.routes.shared import (
    build_sort_clause,
    get_countries,
    get_indicators,
    log_audit,
    safe_float,
)

logger = logging.getLogger(__name__)


class DomainCRUD:
    """Reusable CRUD for a WDI domain fact table + indicator detail table."""

    # ---- Override these in subclasses ----
    blueprint_name: str = ""
    url_prefix: str = ""
    domain_label: str = ""
    domain_icon: str = "fa-database"

    # Table names
    fact_table: str = ""
    detail_table: str = ""
    indicator_pk: str = ""  # e.g. "energy_indicator_id"
    record_pk: str = ""     # e.g. "data_id"
    value_column: str = "indicator_value"
    year_column: str = "year"
    source_column: str = "source_notes"

    # Indicator detail columns (for SELECT)
    indicator_name_col: str = "indicator_name"
    indicator_unit_col: str = "measurement_unit"

    # Extra fact columns beyond (country_id, indicator_id, year, value, source)
    extra_fact_columns: Dict[str, str] = {}  # {db_col: label}

    # Template names
    list_template: str = ""
    form_template: str = ""

    # Sort map: query param value -> SQL column expression
    sort_map: Dict[str, str] = {}

    # Pagination
    per_page: int = 50

    # ---- Blueprint ----
    @classmethod
    def create_blueprint(cls) -> Blueprint:
        """Create a Flask Blueprint with standard CRUD routes."""
        bp = Blueprint(cls.blueprint_name, __name__, url_prefix=cls.url_prefix)

        bp.add_url_rule("/", "list", cls.list_domain)
        bp.add_url_rule("/api/get/<int:id>", "api_get", cls.api_get)
        bp.add_url_rule("/api/add", "api_add", cls.api_add, methods=["POST"])
        bp.add_url_rule("/api/edit/<int:id>", "api_edit", cls.api_edit, methods=["POST"])
        bp.add_url_rule("/api/delete/<int:id>", "api_delete", cls.api_delete, methods=["POST"])

        return bp

    # ---- LIST ----
    @classmethod
    def list_domain(cls) -> str:
        """Render the domain list page with filtering, sorting, and pagination."""
        country_name = request.args.get("country", type=str)
        year_min = request.args.get("year_min", type=int)
        year_max = request.args.get("year_max", type=int)
        sort_by = request.args.get("sort", type=str)
        sort_order = request.args.get("order", default="asc", type=str)
        page = request.args.get("page", default=1, type=int)

        db = get_db()
        cur = db.cursor(dictionary=True)

        try:
            # WHERE clause
            where_clauses = ["1=1"]
            params: List[Any] = []

            if country_name:
                where_clauses.append("c.country_name LIKE %s")
                params.append(f"%{country_name}%")
            if year_min:
                where_clauses.append(f"d.{cls.year_column} >= %s")
                params.append(year_min)
            if year_max:
                where_clauses.append(f"d.{cls.year_column} <= %s")
                params.append(year_max)

            where_sql = " AND ".join(where_clauses)

            # Sorting
            sort_col, sort_dir = build_sort_clause(
                cls.sort_map, "c.country_name", sort_by, sort_order
            )

            # Pagination
            offset = (page - 1) * cls.per_page
            total_sql = (
                f"SELECT COUNT(*) AS cnt FROM {cls.fact_table} d "
                f"JOIN countries c ON c.country_id = d.country_id "
                f"WHERE {where_sql}"
            )
            cur.execute(total_sql, params)
            total = cur.fetchone()["cnt"]

            query = (
                f"SELECT d.*, c.country_name, c.country_code, c.region, "
                f"i.{cls.indicator_name_col} AS indicator_name, "
                f"i.{cls.indicator_unit_col} AS indicator_unit "
                f"FROM {cls.fact_table} d "
                f"JOIN countries c ON c.country_id = d.country_id "
                f"JOIN {cls.detail_table} i ON i.{cls.indicator_pk} = d.{cls.indicator_pk} "
                f"WHERE {where_sql} "
                f"ORDER BY {sort_col} {sort_dir} "
                f"LIMIT %s OFFSET %s"
            )
            params.extend([cls.per_page, offset])
            cur.execute(query, params)
            records = cur.fetchall()

            countries = get_countries()
            indicators = get_indicators(
                cls.detail_table, cls.indicator_pk, cls.indicator_name_col
            )
        finally:
            cur.close()

        total_pages = max(1, (total + cls.per_page - 1) // cls.per_page)

        return render_template(
            cls.list_template,
            records=records,
            countries=countries,
            indicators=indicators,
            total=total,
            page=page,
            total_pages=total_pages,
            per_page=cls.per_page,
            sort_by=sort_by or "",
            sort_order=sort_order,
            country_name=country_name or "",
            year_min=year_min,
            year_max=year_max,
        )

    # ---- API: GET ----
    @classmethod
    def api_get(cls, id: int):
        """Return a single record as JSON."""
        from flask import jsonify

        db = get_db()
        cur = db.cursor(dictionary=True)
        try:
            cur.execute(
                f"SELECT * FROM {cls.fact_table} WHERE {cls.record_pk} = %s",
                (id,),
            )
            record = cur.fetchone()
            if not record:
                return jsonify({"success": False, "error": "Record not found"}), 404
            # Convert numeric values for JSON
            record[cls.value_column] = safe_float(record.get(cls.value_column))
            return jsonify({"success": True, "record": record})
        finally:
            cur.close()

    # ---- API: ADD ----
    @classmethod
    def api_add(cls):
        """Create a new record, log audit, return JSON."""
        from App.routes.login import editor_required
        from flask import jsonify

        @editor_required
        def _add():
            data = request.get_json() or {}
            c_id = data.get("country_id")
            i_id = data.get(cls.indicator_pk)
            year = data.get("year")
            value = data.get(cls.value_column)

            if not all([c_id, i_id, year]):
                return jsonify({"success": False, "error": "Missing required fields"}), 400

            db = get_db()
            cur = db.cursor()
            try:
                cols = ["country_id", cls.indicator_pk, cls.year_column, cls.value_column]
                vals = [c_id, i_id, year, value]

                for col, _ in cls.extra_fact_columns.items():
                    cols.append(col)
                    vals.append(data.get(col))

                if cls.source_column:
                    cols.append(cls.source_column)
                    vals.append(data.get(cls.source_column))

                placeholders = ", ".join(["%s"] * len(cols))
                col_names = ", ".join(cols)
                sql = f"INSERT INTO {cls.fact_table} ({col_names}) VALUES ({placeholders})"
                cur.execute(sql, vals)
                new_id = cur.lastrowid
                log_audit(cur, "CREATE", cls.fact_table, new_id)
                db.commit()
                return jsonify({"success": True, "id": new_id})
            except Exception as e:
                db.rollback()
                logger.error("Add %s error: %s", cls.fact_table, e)
                return jsonify({"success": False, "error": str(e)}), 500
            finally:
                cur.close()

        return _add()

    # ---- API: EDIT ----
    @classmethod
    def api_edit(cls, id: int):
        """Update a record, log audit, return JSON."""
        from App.routes.login import editor_required
        from flask import jsonify

        @editor_required
        def _edit():
            data = request.get_json() or {}
            db = get_db()
            cur = db.cursor(dictionary=True)
            try:
                cur.execute(
                    f"SELECT {cls.record_pk} FROM {cls.fact_table} WHERE {cls.record_pk} = %s",
                    (id,),
                )
                if not cur.fetchone():
                    return jsonify({"success": False, "error": "Record not found"}), 404

                cursor = db.cursor()
                try:
                    sets = [
                        f"{cls.value_column} = %s",
                        f"{cls.year_column} = %s",
                    ]
                    params: List[Any] = [
                        data.get(cls.value_column),
                        data.get("year"),
                    ]
                    if cls.source_column:
                        sets.append(f"{cls.source_column} = %s")
                        params.append(data.get(cls.source_column))

                    params.append(id)
                    sql = (
                        f"UPDATE {cls.fact_table} SET {', '.join(sets)} "
                        f"WHERE {cls.record_pk} = %s"
                    )
                    cursor.execute(sql, params)
                    log_audit(cursor, "UPDATE", cls.fact_table, id)
                    db.commit()
                finally:
                    cursor.close()
                return jsonify({"success": True})
            except Exception as e:
                db.rollback()
                logger.error("Edit %s error: %s", cls.fact_table, e)
                return jsonify({"success": False, "error": str(e)}), 500
            finally:
                cur.close()

        return _edit()

    # ---- API: DELETE ----
    @classmethod
    def api_delete(cls, id: int):
        """Delete a record, log audit, return JSON."""
        from App.routes.login import admin_required
        from flask import jsonify

        @admin_required
        def _delete():
            db = get_db()
            cur = db.cursor(dictionary=True)
            try:
                cur.execute(
                    f"SELECT {cls.record_pk} FROM {cls.fact_table} WHERE {cls.record_pk} = %s",
                    (id,),
                )
                if not cur.fetchone():
                    return jsonify({"success": False, "error": "Record not found"}), 404

                cur.execute(
                    f"DELETE FROM {cls.fact_table} WHERE {cls.record_pk} = %s",
                    (id,),
                )
                log_audit(cur, "DELETE", cls.fact_table, id)
                db.commit()
                return jsonify({"success": True})
            except Exception as e:
                db.rollback()
                logger.error("Delete %s error: %s", cls.fact_table, e)
                return jsonify({"success": False, "error": str(e)}), 500
            finally:
                cur.close()

        return _delete()
