# Generated by Django 5.1.5 on 2025-03-24 16:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("triplog", "0006_rename_user_trip_clerk_remove_trip_user_name"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="trip",
            name="clerk",
        ),
    ]
