from pathlib import Path

import pytest
from django.conf import settings
from django.db import connection

SQL_DIR = Path(settings.BASE_DIR) / 'scripts' / 'sql'


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    """ Apply scripts/sql/*.sql (unmanaged views) to the test database.

    These views back `managed = False` models (e.g. ViewProfile) and are
    not created by `migrate`, so the test database needs them applied
    the same way entrypoint.sh does for dev/prod via `create_db_views`.
    """
    with django_db_blocker.unblock():
        for sql_file in sorted(SQL_DIR.glob('*.sql')):
            statements = [
                statement.strip()
                for statement in sql_file.read_text().split(';')
                if statement.strip()
            ]

            with connection.cursor() as cursor:
                for statement in statements:
                    cursor.execute(statement)
