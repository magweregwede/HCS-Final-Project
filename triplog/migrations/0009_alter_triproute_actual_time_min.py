# Generated by Django 5.1.5 on 2025-03-24 22:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("triplog", "0008_trip_clerk"),
    ]

    operations = [
        migrations.AlterField(
            model_name="triproute",
            name="actual_time_min",
            field=models.IntegerField(blank=True, editable=False, null=True),
        ),
    ]
