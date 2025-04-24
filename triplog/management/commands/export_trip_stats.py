import csv
from django.core.management.base import BaseCommand
from django.conf import settings
import os
from datetime import datetime
from triplog.stats import get_trip_stats
# This script exports trip statistics to a CSV file weekly.
# It uses Django's management command framework to create a custom command.
# The command retrieves trip statistics using the `get_trip_stats` function
# and writes them to a CSV file named `trip_stats_weekly.csv` in the project's root directory.
# The CSV file will have a header row with the statistics keys and a timestamp for when the data was exported.
# The command can be run using Django's management command system.

class Command(BaseCommand):
    help = 'Exports trip statistics to a CSV file weekly'

    def handle(self, *args, **options):
        # Get the stats
        stats = get_trip_stats()
        
        # Define the CSV file path (in the project's root directory)
        csv_file_path = os.path.join(settings.BASE_DIR, 'trip_stats_weekly.csv')
        
        # Prepare the data row with a timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        row_data = {'timestamp': timestamp}
        row_data.update(stats)
        
        # Write to CSV
        file_exists = os.path.exists(csv_file_path)
        
        with open(csv_file_path, mode='a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=row_data.keys())
            
            # Write header if file is new
            if not file_exists:
                writer.writeheader()
            
            # Write the data row
            writer.writerow(row_data)
        
        self.stdout.write(self.style.SUCCESS(f'Successfully exported stats to {csv_file_path}'))