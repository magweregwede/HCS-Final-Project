# your_app/management/commands/export_historical_stats.py
import csv
from django.core.management.base import BaseCommand
from django.conf import settings
import os
import json
from datetime import date, timedelta
from django.utils.timezone import now
from triplog.hist_stats import generate_historical_stats, get_stats_for_date_range

class Command(BaseCommand):
    help = 'Exports comprehensive historical trip statistics'

    def handle(self, *args, **options):
        # Generate all historical stats
        all_stats = generate_historical_stats()
        
        if not all_stats:
            self.stdout.write(self.style.WARNING('No historical data found'))
            return
        
        # Define CSV file path
        csv_file_path = os.path.join(settings.BASE_DIR, 'reports/historical_trip_stats_full.csv')
        
        # Prepare fieldnames and flatten nested structures
        flat_stats = []
        for stat in all_stats:
            flat_stat = {
                'period_type': stat['period_type'],
                'period_start': stat['period_start'],
                'period_end': stat['period_end'],
            }
            
            # Flatten simple metrics
            simple_metrics = [
                'active_deliveries', 'available_drivers', 'total_kilometres',
                'average_trip_time', 'completed_trips', 'ongoing_trips',
                'avg_trips_per_driver', 'total_trucks', 'avg_trips_per_truck',
                'longest_trip_distance', 'longest_trip_time(hrs)',
                'trips_within_estimated_time', 'delayed_trips', 'on_time_rate',
                'percentage_delayed_trips', 'total_delayed_time',
                'average_delay_time', 'total_delayed_time(hrs)',
                'average_delay_time(hrs)', 'weekly_completed_trips',
                'weekly_ongoing_trips', 'weekly_total_kilometres',
                'weekly_average_trip_time', 'weekly_delayed_trips',
                'weekly_on_time_rate', 'monthly_completed_trips',
                'monthly_ongoing_trips', 'monthly_total_kilometres',
                'monthly_average_trip_time', 'monthly_delayed_trips',
                'monthly_on_time_rate'
            ]
            
            for metric in simple_metrics:
                flat_stat[metric] = stat.get(metric, 0)
            
            # Handle nested structures
            flat_stat['top_driver_name'] = stat['top_driver']['name'] if stat['top_driver'] else ''
            flat_stat['top_driver_trips'] = stat['top_driver']['completed_trips'] if stat['top_driver'] else 0
            
            flat_stat['top_truck_plate'] = stat['top_truck']['plate_number'] if stat['top_truck'] else ''
            flat_stat['top_truck_trips'] = stat['top_truck']['total_trips'] if stat['top_truck'] else 0
            
            flat_stat['most_frequent_route'] = stat['most_frequent_route'] or ''
            flat_stat['most_frequent_monthly_route'] = stat['most_frequent_monthly_route'] or ''
            
            # Handle trips_by_status (convert to JSON string)
            flat_stat['trips_by_status'] = json.dumps(stat['trips_by_status'])
            
            # Handle top monthly drivers (convert to JSON string)
            flat_stat['top_monthly_drivers'] = json.dumps(stat['top_monthly_drivers'])
            
            flat_stats.append(flat_stat)
        
        # Write to CSV
        with open(csv_file_path, mode='w', newline='') as csvfile:
            if flat_stats:
                fieldnames = flat_stats[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(flat_stats)
        
        self.stdout.write(self.style.SUCCESS(
            f'Successfully exported {len(all_stats)} periods to {csv_file_path}'
        ))

def generate_historical_stats(start_date=date(2024, 2, 1)):
    """Generate weekly and monthly stats from start_date to now"""
    end_date = now().date()
    all_stats = []

    # Generate monthly stats first
    current_month_date = start_date.replace(day=1)  # Start from the first day of the month
    while current_month_date <= end_date:
        # Calculate the start of the next month
        if current_month_date.month == 12:
            next_month = current_month_date.replace(year=current_month_date.year + 1, month=1, day=1)
        else:
            next_month = current_month_date.replace(month=current_month_date.month + 1, day=1)

        # Calculate the end of the current month
        month_end = min(next_month - timedelta(days=1), end_date)

        # Get monthly stats
        monthly_stats = get_stats_for_date_range(current_month_date, month_end)
        monthly_stats['period_type'] = 'monthly'
        all_stats.append(monthly_stats)

        # Move to the next month
        current_month_date = next_month

    # Generate weekly stats separately (Monday to Sunday)
    # Find the first Monday on or after the start_date
    current_week_start = start_date
    if current_week_start.weekday() != 0:  # If not Monday
        current_week_start = current_week_start - timedelta(days=current_week_start.weekday())

    while current_week_start <= end_date:
        # Calculate the end of the current week (Sunday)
        week_end = min(current_week_start + timedelta(days=6), end_date)

        # Get weekly stats
        weekly_stats = get_stats_for_date_range(current_week_start, week_end)
        weekly_stats['period_type'] = 'weekly'
        all_stats.append(weekly_stats)

        # Move to the next Monday
        current_week_start = current_week_start + timedelta(days=7)

    return all_stats