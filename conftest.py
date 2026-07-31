from pathlib import Path

import pytest

SQL_DIR = Path(__file__).resolve().parent / "scripts" / "sql"


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    """Apply hand-maintained SQL views that are not managed by Django migrations.

    Custom apps in this project have no migrations (schema is synced directly
    from models), so views like ``view_profile`` are never created for the
    test database unless applied here, matching how they are applied to
    real databases via the scripts in scripts/sql/.
    """
    from django.db import connection

    with django_db_blocker.unblock():
        with connection.cursor() as cursor:
            for statement in (SQL_DIR / "view_profile.sql").read_text().split(";"):
                statement = statement.strip()
                if statement:
                    cursor.execute(statement)
