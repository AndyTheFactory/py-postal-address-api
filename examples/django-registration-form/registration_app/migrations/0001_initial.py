# Generated manually for standalone example.

from django.db import migrations, models


class Migration(migrations.Migration):
    """Initial migration for the User model in the registration_app."""

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
                ),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("first_name", models.CharField(max_length=100)),
                ("last_name", models.CharField(max_length=100)),
                ("street", models.CharField(blank=True, max_length=255)),
                ("house_number", models.CharField(blank=True, max_length=10)),
                ("postal_code", models.CharField(blank=True, max_length=10)),
                ("city", models.CharField(blank=True, max_length=100)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"verbose_name": "User", "verbose_name_plural": "Users"},
        ),
    ]
