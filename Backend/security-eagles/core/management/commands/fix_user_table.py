from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Fix the core_user table to match the model'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # Add missing columns to core_user table
            missing_columns = [
                ('sso_provider', 'VARCHAR(255)'),
                ('sso_id', 'VARCHAR(255)'),
                ('score', 'INTEGER DEFAULT 0'),
                ('total_points', 'INTEGER DEFAULT 0'),
                ('available_points', 'INTEGER DEFAULT 0'),
                ('cv', 'VARCHAR(100)'),
                ('github', 'VARCHAR(200)'),
                ('linkedin', 'VARCHAR(200)'),
                ('portfolio_url', 'VARCHAR(200)'),
                ('phone', 'VARCHAR(20)'),
                ('city', 'VARCHAR(100)'),
                ('type', 'VARCHAR(20) DEFAULT \'public\''),
                ('created_by_id', 'INTEGER'),
                ('meta_data', 'JSONB'),
            ]
            
            for column_name, column_def in missing_columns:
                try:
                    # Check if column exists
                    cursor.execute("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = 'core_user' AND column_name = %s
                    """, [column_name])
                    
                    if not cursor.fetchone():
                        # Add the column
                        cursor.execute(f"ALTER TABLE core_user ADD COLUMN {column_name} {column_def}")
                        self.stdout.write(f"Added column: {column_name}")
                    else:
                        self.stdout.write(f"Column already exists: {column_name}")
                        
                except Exception as e:
                    self.stdout.write(f"Error adding column {column_name}: {e}")
            
            # Remove cv_url column if it exists (replaced by cv)
            try:
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'core_user' AND column_name = 'cv_url'
                """)
                
                if cursor.fetchone():
                    cursor.execute("ALTER TABLE core_user DROP COLUMN cv_url")
                    self.stdout.write("Removed column: cv_url")
                    
            except Exception as e:
                self.stdout.write(f"Error removing cv_url column: {e}")
                
            self.stdout.write(
                self.style.SUCCESS('Successfully updated core_user table')
            )
