"""
Flask-Admin integration for OrderFlow (additive — does not replace database.py).

Reflects the existing orderflow.db schema via SQLAlchemy automap for read/write in /admin.
"""

import os

from flask import request
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from sqlalchemy.ext.automap import automap_base

import database as legacy_db

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_DB_FILE = os.path.join(_BASE_DIR, legacy_db.DB)

db = SQLAlchemy()


class OrderFlowModelView(ModelView):
    """Model view for reflected tables (uppercase column names)."""

    page_size = 25
    can_view_details = True
    can_export = True

    def scaffold_list_columns(self):
        return [col.key for col in self.model.__mapper__.columns]

    def scaffold_form_columns(self):
        return [col.key for col in self.model.__mapper__.columns]


class SQLConsoleView(BaseView):
    """Run raw SQL against orderflow.db from the browser."""

    @expose("/", methods=["GET", "POST"])
    def index(self):
        sql = ""
        columns = []
        rows = []
        message = None
        error = None
        rowcount = None

        if request.method == "POST":
            sql = (request.form.get("sql") or "").strip()
            if not sql:
                error = "Enter a SQL statement."
            else:
                try:
                    result = db.session.execute(text(sql))
                    if result.returns_rows:
                        rows = [dict(row._mapping) for row in result.fetchall()]
                        columns = list(rows[0].keys()) if rows else list(result.keys())
                    else:
                        db.session.commit()
                        rowcount = result.rowcount
                        message = f"Query executed successfully. Rows affected: {rowcount}"
                except Exception as exc:
                    db.session.rollback()
                    error = str(exc)

        return self.render(
            "admin/sql_console.html",
            sql=sql,
            columns=columns,
            rows=rows,
            message=message,
            error=error,
            rowcount=rowcount,
        )


def init_admin(app):
    """Attach Flask-Admin at /admin using the same SQLite file as database.py."""
    app.config.setdefault("SECRET_KEY", os.environ.get("SECRET_KEY", "orderflow-admin-dev-key"))
    app.config.setdefault("SQLALCHEMY_DATABASE_URI", f"sqlite:///{_DB_FILE}")
    app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)
    app.config.setdefault(
        "SQLALCHEMY_ENGINE_OPTIONS",
        {"connect_args": {"check_same_thread": False}},
    )

    db.init_app(app)

    with app.app_context():
        base = automap_base()
        base.prepare(autoload_with=db.engine)

        admin = Admin(
            app,
            name="OrderFlow Admin",
            url="/admin",
            endpoint="admin",
        )

        table_views = [
            ("customers", "Customers"),
            ("products", "Products"),
            ("orders", "Orders"),
            ("order_items", "Order Items"),
        ]

        for table_name, label in table_views:
            model = getattr(base.classes, table_name, None)
            if model is None:
                continue
            admin.add_view(
                OrderFlowModelView(
                    model,
                    db.session,
                    name=label,
                    endpoint=f"admin_{table_name}",
                )
            )

        admin.add_view(SQLConsoleView(name="SQL Console", endpoint="admin_sql"))

    return admin
