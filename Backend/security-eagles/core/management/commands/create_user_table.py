from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Create the core_user table manually'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # Check if table exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'core_user'
                );
            """)
            table_exists = cursor.fetchone()[0]
            
            if table_exists:
                self.stdout.write(
                    self.style.SUCCESS('core_user table already exists')
                )
            else:
                # Create the table based on the initial migration
                cursor.execute("""
                    CREATE TABLE core_user (
                        id SERIAL PRIMARY KEY,
                        password VARCHAR(128) NOT NULL,
                        last_login TIMESTAMP WITH TIME ZONE,
                        is_superuser BOOLEAN NOT NULL,
                        username VARCHAR(150) NOT NULL UNIQUE,
                        first_name VARCHAR(150) NOT NULL,
                        last_name VARCHAR(150) NOT NULL,
                        email VARCHAR(254) NOT NULL,
                        is_staff BOOLEAN NOT NULL,
                        is_active BOOLEAN NOT NULL,
                        date_joined TIMESTAMP WITH TIME ZONE NOT NULL,
                        bio TEXT,
                        profile_pic VARCHAR(100),
                        cv_url VARCHAR(200),
                        github_url VARCHAR(200),
                        linkedin_url VARCHAR(200),
                        discord_username VARCHAR(100),
                        phone_number VARCHAR(20),
                        created_at TIMESTAMP WITH TIME ZONE NOT NULL,
                        updated_at TIMESTAMP WITH TIME ZONE NOT NULL
                    );
                """)
                
                # Create indexes
                cursor.execute("CREATE INDEX core_user_username_idx ON core_user (username);")
                cursor.execute("CREATE INDEX core_user_email_idx ON core_user (email);")
                
                self.stdout.write(
                    self.style.SUCCESS('Successfully created core_user table')
                )
