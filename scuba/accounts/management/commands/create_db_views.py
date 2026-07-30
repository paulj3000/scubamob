from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection

SQL_DIR = Path(settings.BASE_DIR) / 'scripts' / 'sql'


class Command(BaseCommand):
    help = 'Create or replace database views defined in scripts/sql/*.sql'

    def handle(self, *args, **options) -> None:
        for sql_file in sorted(SQL_DIR.glob('*.sql')):
            self.stdout.write(f'Applying {sql_file.name}')
            statements = [
                statement.strip()
                for statement in sql_file.read_text().split(';')
                if statement.strip()
            ]

            with connection.cursor() as cursor:
                for statement in statements:
                    cursor.execute(statement)
