# Generated by Django 5.1.5 on 2025-06-02 13:47

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("triplog", "0017_driverleaderboard_monthlydriverranking"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="DriverAvailability",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "is_available",
                    models.BooleanField(
                        default=True,
                        help_text="Whether the driver is currently available for trips",
                    ),
                ),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "notes",
                    models.TextField(
                        blank=True,
                        help_text="Optional notes about availability status",
                        null=True,
                    ),
                ),
                (
                    "triplog_driver",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="availability",
                        to="triplog.driver",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="driver_availability",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Driver Availability",
                "verbose_name_plural": "Driver Availabilities",
            },
        ),
    ]
