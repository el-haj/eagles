from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Fix migration dependency issues'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # Check if core.0001_initial is in the migration table
            cursor.execute(
                "SELECT COUNT(*) FROM django_migrations WHERE app = 'core' AND name = '0001_initial'"
            )
            core_exists = cursor.fetchone()[0]
            
            if core_exists == 0:
                # Insert the core migration as applied
                cursor.execute(
                    "INSERT INTO django_migrations (app, name, applied) VALUES ('core', '0001_initial', NOW())"
                )
                self.stdout.write(
                    self.style.SUCCESS('Successfully marked core.0001_initial as applied')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('core.0001_initial already exists in migration table')
                )
            
            # Show current migration status
            cursor.execute(
                "SELECT app, name, applied FROM django_migrations WHERE app IN ('admin', 'core') ORDER BY applied"
            )
            migrations = cursor.fetchall()
            
            self.stdout.write('\nCurrent migration status:')
            for app, name, applied in migrations:
                self.stdout.write(f'  {app}.{name} - {applied}')
