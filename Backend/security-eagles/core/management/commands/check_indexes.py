from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Check what indexes exist in the database'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # Check indexes on jobs_job table
            cursor.execute("""
                SELECT indexname, tablename 
                FROM pg_indexes 
                WHERE tablename = 'jobs_job'
                ORDER BY indexname;
            """)
            
            indexes = cursor.fetchall()
            
            self.stdout.write("Indexes on jobs_job table:")
            for index_name, table_name in indexes:
                self.stdout.write(f"  - {index_name}")
                
            if not indexes:
                self.stdout.write("  No indexes found on jobs_job table")
