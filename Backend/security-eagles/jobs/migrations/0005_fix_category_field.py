# Generated manually to fix category field

from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0004_job_category_fk'),
    ]

    operations = [
        # This migration reflects the manual database changes:
        # 1. Dropped the old 'category' CharField
        # 2. Renamed 'category_fk_id' to 'category_id'
        # 3. Updated the model to use the ForeignKey properly
        migrations.RunSQL(
            "-- Manual database changes already applied",
            reverse_sql="-- Cannot reverse manual changes"
        ),
    ]
