from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Check what columns exist in the jobs_job table'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # Check columns on jobs_job table
            cursor.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'jobs_job'
                ORDER BY ordinal_position;
            """)
            
            columns = cursor.fetchall()
            
            self.stdout.write("Columns in jobs_job table:")
            for column_name, data_type, is_nullable in columns:
                self.stdout.write(f"  - {column_name} ({data_type}, nullable: {is_nullable})")
                
            if not columns:
                self.stdout.write("  No columns found in jobs_job table")
