# Generated by Django 5.1.5 on 2025-03-26 21:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("triplog", "0010_trip_route_triproute_driver_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="trip",
            name="route",
        ),
        migrations.RemoveField(
            model_name="triproute",
            name="driver",
        ),
    ]
