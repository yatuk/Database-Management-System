"""REST API blueprint for the React SPA frontend.

All endpoints return JSON. State-changing endpoints require
``X-CSRF-Token`` header matching the session CSRF token.
"""

import logging
from typing import Any, Dict, List, Optional

from flask import Blueprint, abort, jsonify, request, session

from App.db import get_db
from App.routes.login import admin_required, editor_required, get_current_role
from App.routes.shared import get_countries, get_indicators, log_audit, safe_float

logger = logging.getLogger(__name__)

api_bp = Blueprint("api", __name__, url_prefix="/api")

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

PER_PAGE = 50


def _paginate_query(
    base_sql: str,
    count_sql: str,
    params: List[Any],
    page: int,
    per_page: int = PER_PAGE,
) -> Dict[str, Any]:
    """Execute a paginated query and return {data, total, page, total_pages}."""
    db = get_db()
    cur = db.cursor(dictionary=True)
    try:
        cur.execute(count_sql, params)
        total = cur.fetchone()["cnt"]

        offset = (page - 1) * per_page
        sql = f"{base_sql} LIMIT %s OFFSET %s"
        cur.execute(sql, params + [per_page, offset])
        data = cur.fetchall()
    finally:
        cur.close()

    return {
        "data": data,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": max(1, (total + per_page - 1) // per_page),
    }


def _build_where(params: List[Any], **filters: Any) -> str:
    """Build a WHERE clause from keyword filters. Populates *params* in-place."""
    clauses = ["1=1"]
    for col, val in filters.items():
        if val is not None and val != "":
            if isinstance(val, str) and col.endswith("_like"):
                clauses.append(f"{col[:-5]} LIKE %s")
                params.append(f"%{val}%")
            else:
                clauses.append(f"{col} = %s")
                params.append(val)
    return " AND ".join(clauses)


def _single_row(table: str, pk: str, id: int) -> Optional[Dict[str, Any]]:
    """Return a single row or None."""
    db = get_db()
    cur = db.cursor(dictionary=True)
    try:
        cur.execute(f"SELECT * FROM {table} WHERE {pk} = %s", (id,))
        return cur.fetchone()
    finally:
        cur.close()


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------


@api_bp.route("/auth/me")
def auth_me():
    """Return the current authenticated user or 401."""
    if "student_id" not in session:
        return jsonify({"authenticated": False, "role": "viewer"})
    return jsonify(
        {
            "authenticated": True,
            "student_id": session.get("student_id"),
            "student_number": session.get("student_number"),
            "role": get_current_role(),
        }
    )


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------


@api_bp.route("/dashboard")
def dashboard():
    """Return dashboard coverage stats."""
    db = get_db()
    cur = db.cursor(dictionary=True)

    result: Dict[str, Any] = {}
    try:
        cur.execute("SELECT COUNT(*) AS cnt FROM countries")
        result["countries"] = cur.fetchone()["cnt"]

        domains = [
            ("health", "health_system", "health_indicator_details", "health_indicator_id"),
            ("energy", "energy_data", "energy_indicator_details", "energy_indicator_id"),
            ("freshwater", "freshwater_data", "freshwater_indicator_details", "freshwater_indicator_id"),
            ("ghg", "greenhouse_emissions", "ghg_indicator_details", "ghg_indicator_id"),
            ("sustainability", "sustainability_data", "sustainability_indicator_details", "sus_indicator_id"),
        ]

        for name, fact, detail, pk in domains:
            cur.execute(f"SELECT COUNT(*) AS cnt FROM {detail}")
            ind_cnt = cur.fetchone()["cnt"]
            try:
                cur.execute(
                    f"SELECT MIN(year) AS min_year, MAX(year) AS max_year, COUNT(*) AS records "
                    f"FROM {fact} WHERE indicator_value IS NOT NULL"
                )
                stats = cur.fetchone() or {}
            except Exception:
                stats = {}
            result[name] = {
                "indicators": ind_cnt,
                "min_year": stats.get("min_year"),
                "max_year": stats.get("max_year"),
                "records": stats.get("records", 0),
            }
    finally:
        cur.close()

    return jsonify(result)


# ---------------------------------------------------------------------------
# Countries
# ---------------------------------------------------------------------------


@api_bp.route("/countries")
def api_countries():
    """List countries with search and data availability."""
    search = request.args.get("q", type=str)
    db = get_db()
    cur = db.cursor(dictionary=True)

    try:
        where = "1=1"
        params: List[Any] = []
        if search:
            where = "(LOWER(c.country_name) LIKE %s OR LOWER(c.country_code) LIKE %s)"
            pattern = f"%{search.lower()}%"
            params = [pattern, pattern]

        cur.execute(
            f"""
            SELECT c.*,
              COALESCE((SELECT COUNT(*) FROM health_system h WHERE h.country_id=c.country_id),0)
              + COALESCE((SELECT COUNT(*) FROM energy_data e WHERE e.country_id=c.country_id),0)
              + COALESCE((SELECT COUNT(*) FROM freshwater_data f WHERE f.country_id=c.country_id),0)
              + COALESCE((SELECT COUNT(*) FROM greenhouse_emissions g WHERE g.country_id=c.country_id),0)
              + COALESCE((SELECT COUNT(*) FROM sustainability_data s WHERE s.country_id=c.country_id),0)
              AS data_count
            FROM countries c
            WHERE {where}
            ORDER BY c.country_name
            """,
            params,
        )
        countries = cur.fetchall()

        cur.execute(
            "SELECT DISTINCT region FROM countries WHERE region IS NOT NULL AND region != '' ORDER BY region"
        )
        regions = [r["region"] for r in cur.fetchall()]

        cur.execute("SELECT COUNT(*) AS cnt FROM countries")
        total = cur.fetchone()["cnt"]
    finally:
        cur.close()

    return jsonify({"countries": countries, "regions": regions, "total": total})


@api_bp.route("/countries/<int:country_id>")
def api_country_profile(country_id: int):
    """Return country profile with data from all 5 domains."""
    db = get_db()
    cur = db.cursor(dictionary=True)

    try:
        cur.execute("SELECT * FROM countries WHERE country_id = %s", (country_id,))
        country = cur.fetchone()
        if not country:
            abort(404)

        profile = {"country": country, "domains": {}}

        domain_queries = [
            ("health", "health_system", "health_indicator_details", "health_indicator_id", "indicator_value", "row_id"),
            ("energy", "energy_data", "energy_indicator_details", "energy_indicator_id", "indicator_value", "data_id"),
            ("freshwater", "freshwater_data", "freshwater_indicator_details", "freshwater_indicator_id", "indicator_value", "data_id"),
            ("ghg", "greenhouse_emissions", "ghg_indicator_details", "ghg_indicator_id", "indicator_value", "row_id"),
            ("sustainability", "sustainability_data", "sustainability_indicator_details", "sus_indicator_id", "indicator_value", "data_id"),
        ]

        for name, fact, detail, fk, val_col, pk in domain_queries:
            cur.execute(
                f"""
                SELECT d.{pk} AS id, d.year, d.{val_col} AS value,
                       d.source_notes AS note,
                       i.indicator_name AS indicator
                FROM {fact} d
                JOIN {detail} i ON i.{fk} = d.{fk}
                WHERE d.country_id = %s
                ORDER BY d.year DESC
                LIMIT 500
                """,
                (country_id,),
            )
            profile["domains"][name] = cur.fetchall()

    finally:
        cur.close()

    return jsonify(profile)


@api_bp.route("/countries/region/<string:region_name>")
def api_region_profile(region_name: str):
    """Return region profile with aggregated data across all 5 domains."""
    db = get_db()
    cur = db.cursor(dictionary=True)

    try:
        cur.execute(
            "SELECT DISTINCT region FROM countries WHERE region = %s LIMIT 1",
            (region_name,),
        )
        if not cur.fetchone():
            abort(404)

        result: Dict[str, Any] = {"region": region_name, "domains": {}}

        domain_queries = [
            ("health", "health_system", "health_indicator_details", "health_indicator_id", "indicator_value"),
            ("energy", "energy_data", "energy_indicator_details", "energy_indicator_id", "indicator_value"),
            ("freshwater", "freshwater_data", "freshwater_indicator_details", "freshwater_indicator_id", "indicator_value"),
            ("ghg", "greenhouse_emissions", "ghg_indicator_details", "ghg_indicator_id", "indicator_value"),
            ("sustainability", "sustainability_data", "sustainability_indicator_details", "sus_indicator_id", "indicator_value"),
        ]

        for name, fact, detail, fk, val in domain_queries:
            cur.execute(
                f"""
                SELECT i.indicator_name AS indicator, d.year,
                       AVG(d.{val}) AS avg_value,
                       MIN(d.{val}) AS min_value,
                       MAX(d.{val}) AS max_value,
                       COUNT(DISTINCT d.country_id) AS country_count
                FROM {fact} d
                JOIN {detail} i ON i.{fk} = d.{fk}
                JOIN countries c ON c.country_id = d.country_id
                WHERE c.region = %s AND d.{val} IS NOT NULL
                GROUP BY i.indicator_name, d.year
                ORDER BY d.year DESC
                LIMIT 500
                """,
                (region_name,),
            )
            result["domains"][name] = cur.fetchall()

        cur.execute(
            "SELECT country_id, country_name, country_code FROM countries WHERE region = %s ORDER BY country_name",
            (region_name,),
        )
        result["countries"] = cur.fetchall()

    finally:
        cur.close()

    return jsonify(result)


# ---------------------------------------------------------------------------
# Domain CRUD (energy, freshwater, ghg, health, sustainability)
# ---------------------------------------------------------------------------

_DOMAIN_CONFIG = {
    "energy": {
        "fact": "energy_data",
        "detail": "energy_indicator_details",
        "fk": "energy_indicator_id",
        "pk": "data_id",
        "val": "indicator_value",
        "year": "year",
        "source": "data_source",
        "extra_cols": {},
    },
    "freshwater": {
        "fact": "freshwater_data",
        "detail": "freshwater_indicator_details",
        "fk": "freshwater_indicator_id",
        "pk": "data_id",
        "val": "indicator_value",
        "year": "year",
        "source": "source_notes",
        "extra_cols": {},
    },
    "ghg": {
        "fact": "greenhouse_emissions",
        "detail": "ghg_indicator_details",
        "fk": "ghg_indicator_id",
        "pk": "row_id",
        "val": "indicator_value",
        "year": "year",
        "source": "source_notes",
        "extra_cols": {
            "share_of_total_pct": "share_of_total_pct",
            "uncertainty_pct": "uncertainty_pct",
        },
    },
    "health": {
        "fact": "health_system",
        "detail": "health_indicator_details",
        "fk": "health_indicator_id",
        "pk": "row_id",
        "val": "indicator_value",
        "year": "year",
        "source": "source_notes",
        "extra_cols": {},
    },
    "sustainability": {
        "fact": "sustainability_data",
        "detail": "sustainability_indicator_details",
        "fk": "sus_indicator_id",
        "pk": "data_id",
        "val": "indicator_value",
        "year": "year",
        "source": "source_note",
        "extra_cols": {},
    },
}


def _domain_config(domain: str) -> Dict[str, Any]:
    cfg = _DOMAIN_CONFIG.get(domain)
    if not cfg:
        abort(404, description=f"Unknown domain: {domain}")
    return cfg


@api_bp.route("/<string:domain>/list")
def api_domain_list(domain: str):
    """Paginated list of domain records with joined country/indicator names."""
    cfg = _domain_config(domain)
    f, d, fk, pk, val, year, src = (
        cfg["fact"], cfg["detail"], cfg["fk"], cfg["pk"],
        cfg["val"], cfg["year"], cfg["source"],
    )

    # filters
    country = request.args.get("country", type=str)
    year_val = request.args.get("year", type=int)
    year_min = request.args.get("year_min", type=int)
    year_max = request.args.get("year_max", type=int)
    sort_by = request.args.get("sort_by", default=year, type=str)
    order = request.args.get("order", default="desc", type=str)
    page = request.args.get("page", default=1, type=int)

    allowed_sort = {
        "id": f"f.{pk}",
        "country": "c.country_name",
        "region": "c.region",
        "code": "c.country_code",
        "indicator": "i.indicator_name",
        "year": f"f.{year}",
        "value": f"f.{val}",
    }
    sort_col = allowed_sort.get(sort_by, f"f.{year}")
    sort_dir = "ASC" if order.upper() == "ASC" else "DESC"
    params: List[Any] = []
    where = _build_where(
        params,
        country_name_like=country,
        **{f"f.{year}": year_val},
        **{f"f.{year}_gte" if year_min else "": year_min},
        **{f"f.{year}_lte" if year_max else "": year_max},
    )
    # fix for range filters (hack: _build_where doesn't support >=)
    where = "1=1"
    params = []
    if country:
        where += " AND c.country_name LIKE %s"
        params.append(f"%{country}%")
    if year_val is not None:
        where += f" AND f.{year} = %s"
        params.append(year_val)
    if year_min is not None:
        where += f" AND f.{year} >= %s"
        params.append(year_min)
    if year_max is not None:
        where += f" AND f.{year} <= %s"
        params.append(year_max)

    base = (
        f"SELECT f.*, c.country_name, c.country_code, c.region, "
        f"i.indicator_name, i.indicator_code "
        f"FROM {f} f "
        f"JOIN countries c ON c.country_id = f.country_id "
        f"JOIN {d} i ON i.{fk} = f.{fk} "
        f"WHERE {where} "
        f"ORDER BY {sort_col} {sort_dir} "
    )
    count_sql = (
        f"SELECT COUNT(*) AS cnt FROM {f} f "
        f"JOIN countries c ON c.country_id = f.country_id "
        f"WHERE {where}"
    )

    return jsonify(_paginate_query(base, count_sql, params, page))


@api_bp.route("/<string:domain>/get/<int:id>")
def api_domain_get(domain: str, id: int):
    """Return a single domain record with joined names."""
    cfg = _domain_config(domain)
    f, d, fk, pk = cfg["fact"], cfg["detail"], cfg["fk"], cfg["pk"]

    db = get_db()
    cur = db.cursor(dictionary=True)
    try:
        cur.execute(
            f"""
            SELECT f.*, c.country_name, c.country_code, c.region,
                   i.indicator_name
            FROM {f} f
            JOIN countries c ON c.country_id = f.country_id
            JOIN {d} i ON i.{fk} = f.{fk}
            WHERE f.{pk} = %s
            """,
            (id,),
        )
        record = cur.fetchone()
        if not record:
            return jsonify({"success": False, "error": "Record not found"}), 404
        return jsonify({"success": True, "record": record})
    finally:
        cur.close()


@api_bp.route("/<string:domain>/add", methods=["POST"])
@editor_required
def api_domain_add(domain: str):
    """Create a new domain record."""
    cfg = _domain_config(domain)
    f, fk, pk, val, year, src = (
        cfg["fact"], cfg["fk"], cfg["pk"], cfg["val"],
        cfg["year"], cfg["source"],
    )

    data = request.get_json() or {}
    c_id = data.get("country_id")
    i_id = data.get(fk)
    yr = data.get(year)
    vl = data.get(val)

    if not all([c_id, i_id, yr, vl is not None]):
        return jsonify({"success": False, "error": "Missing required fields"}), 400

    db = get_db()
    cur = db.cursor()
    try:
        cols = ["country_id", fk, year, val]
        vals = [c_id, i_id, yr, vl]

        for col in cfg["extra_cols"]:
            cols.append(col)
            vals.append(data.get(col))

        cols.append(src)
        vals.append(data.get(src))

        placeholders = ", ".join(["%s"] * len(cols))
        sql = f"INSERT INTO {f} ({', '.join(cols)}) VALUES ({placeholders})"
        cur.execute(sql, vals)
        new_id = cur.lastrowid
        log_audit(cur, "CREATE", f, new_id)
        db.commit()

        record = _single_row(f, pk, new_id)
        return jsonify({"success": True, "record": record}), 201
    except Exception as e:
        db.rollback()
        logger.error("Add %s error: %s", f, e)
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        cur.close()


@api_bp.route("/<string:domain>/edit/<int:id>", methods=["POST"])
@editor_required
def api_domain_edit(domain: str, id: int):
    """Update a domain record."""
    cfg = _domain_config(domain)
    f, pk, val, year, src = cfg["fact"], cfg["pk"], cfg["val"], cfg["year"], cfg["source"]

    data = request.get_json() or {}
    db = get_db()
    cur = db.cursor(dictionary=True)
    try:
        cur.execute(f"SELECT {pk} FROM {f} WHERE {pk} = %s", (id,))
        if not cur.fetchone():
            return jsonify({"success": False, "error": "Record not found"}), 404

        cursor = db.cursor()
        try:
            sets = [f"{val} = %s", f"{year} = %s", f"{src} = %s"]
            params: List[Any] = [data.get(val), data.get(year), data.get(src, "")]
            params.append(id)
            sql = f"UPDATE {f} SET {', '.join(sets)} WHERE {pk} = %s"
            cursor.execute(sql, params)
            log_audit(cursor, "UPDATE", f, id)
            db.commit()
        finally:
            cursor.close()

        record = _single_row(f, pk, id)
        return jsonify({"success": True, "record": record})
    except Exception as e:
        db.rollback()
        logger.error("Edit %s error: %s", f, e)
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        cur.close()


@api_bp.route("/<string:domain>/delete/<int:id>", methods=["POST"])
@admin_required
def api_domain_delete(domain: str, id: int):
    """Delete a domain record (admin only)."""
    cfg = _domain_config(domain)
    f, pk = cfg["fact"], cfg["pk"]

    db = get_db()
    cur = db.cursor(dictionary=True)
    try:
        cur.execute(f"SELECT {pk} FROM {f} WHERE {pk} = %s", (id,))
        if not cur.fetchone():
            return jsonify({"success": False, "error": "Record not found"}), 404

        cur.execute(f"DELETE FROM {f} WHERE {pk} = %s", (id,))
        log_audit(cur, "DELETE", f, id)
        db.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.rollback()
        logger.error("Delete %s error: %s", f, e)
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        cur.close()


# ---------------------------------------------------------------------------
# Autocomplete & lookups
# ---------------------------------------------------------------------------


@api_bp.route("/<string:domain>/indicators")
def api_domain_indicators(domain: str):
    """Return indicator list for a domain."""
    cfg = _domain_config(domain)
    d, fk = cfg["detail"], cfg["fk"]
    return jsonify(
        get_indicators(d, fk, "indicator_name")
    )


@api_bp.route("/<string:domain>/countries")
def api_domain_countries(domain: str):
    """Return countries with data in the given domain."""
    cfg = _domain_config(domain)
    f = cfg["fact"]
    db = get_db()
    cur = db.cursor(dictionary=True)
    try:
        cur.execute(
            f"""
            SELECT DISTINCT c.country_id, c.country_name, c.country_code, c.region
            FROM countries c
            JOIN {f} f ON f.country_id = c.country_id
            ORDER BY c.country_name
            """
        )
        return jsonify(cur.fetchall())
    finally:
        cur.close()


@api_bp.route("/<string:domain>/years")
def api_domain_years(domain: str):
    """Return distinct years available in a domain."""
    cfg = _domain_config(domain)
    f, yr = cfg["fact"], cfg["year"]
    db = get_db()
    cur = db.cursor(dictionary=True)
    try:
        cur.execute(
            f"SELECT DISTINCT {yr} AS year FROM {f} ORDER BY {yr} DESC"
        )
        return jsonify([r["year"] for r in cur.fetchall()])
    finally:
        cur.close()


@api_bp.route("/countries/autocomplete")
def api_countries_autocomplete():
    """Autocomplete countries by name or code."""
    q = request.args.get("q", type=str, default="")
    db = get_db()
    cur = db.cursor(dictionary=True)
    try:
        cur.execute(
            """
            SELECT country_id, country_name, country_code, region
            FROM countries
            WHERE country_name LIKE %s OR country_code LIKE %s
            ORDER BY country_name
            LIMIT 20
            """,
            (f"%{q}%", f"%{q}%"),
        )
        return jsonify(cur.fetchall())
    finally:
        cur.close()
