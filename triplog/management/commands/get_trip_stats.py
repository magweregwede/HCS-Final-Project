from django.core.management.base import BaseCommand
from triplog.stats import get_trip_stats

class Command(BaseCommand):
    help = 'Get trip statistics'

    def handle(self, *args, **kwargs):
        stats = get_trip_stats()
        self.stdout.write("\nTrip Statistics:\n")
        for key, value in stats.items():
            self.stdout.write(f"{key.replace('_', ' ').title()}: {value}")

# run with python manage.py get_trip_stats
