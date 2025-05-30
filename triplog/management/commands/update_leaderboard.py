import csv
import re
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from triplog.models import DriverLeaderboard, MonthlyDriverRanking
import os

class Command(BaseCommand):
    help = 'Updates driver leaderboard from historical stats CSV'
    
    def handle(self, *args, **options):
        csv_file_path = os.path.join(settings.BASE_DIR, 'reports/historical_trip_stats_full.csv')
        
        if not os.path.exists(csv_file_path):
            self.stdout.write(self.style.ERROR('CSV file not found'))
            return
        
        # Clear existing leaderboard data
        DriverLeaderboard.objects.all().delete()
        MonthlyDriverRanking.objects.all().delete()
        
        points_mapping = {1: 10, 2: 6, 3: 3}
        driver_points = {}
        driver_rank_counts = {}
        
        with open(csv_file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                # Only process monthly data with top drivers
                if (row['period_type'] == 'monthly' and 
                    row['top_monthly_drivers'] and 
                    row['top_monthly_drivers'] != '[]'):
                    
                    month_date = datetime.strptime(row['period_start'], '%Y-%m-%d').date()
                    top_drivers_str = row['top_monthly_drivers']
                    
                    # Parse the top drivers string
                    # Format: ["Driver Name (X trips)", "Driver Name (Y trips)", ...]
                    drivers = self.parse_top_drivers(top_drivers_str)
                    
                    # Award points based on ranking
                    for rank, driver_info in enumerate(drivers, 1):
                        if rank > 3:  # Only top 3 get points
                            break
                            
                        driver_name = driver_info['name']
                        trips_count = driver_info['trips']
                        points = points_mapping[rank]
                        
                        # Update driver points
                        if driver_name not in driver_points:
                            driver_points[driver_name] = 0
                            driver_rank_counts[driver_name] = {1: 0, 2: 0, 3: 0}
                        
                        driver_points[driver_name] += points
                        driver_rank_counts[driver_name][rank] += 1
                        
                        # Create monthly ranking record
                        MonthlyDriverRanking.objects.create(
                            driver_name=driver_name,
                            month=month_date,
                            rank=rank,
                            trips_completed=trips_count,
                            points_earned=points
                        )
        
        # Create leaderboard entries
        for driver_name, total_points in driver_points.items():
            DriverLeaderboard.objects.create(
                driver_name=driver_name,
                total_points=total_points,
                rank_1_count=driver_rank_counts[driver_name][1],
                rank_2_count=driver_rank_counts[driver_name][2],
                rank_3_count=driver_rank_counts[driver_name][3]
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully updated leaderboard with {len(driver_points)} drivers'
            )
        )
    
    def parse_top_drivers(self, drivers_str):
        """Parse the top drivers string and extract driver names and trip counts"""
        drivers = []
        
        # Remove brackets and quotes, then split by comma
        clean_str = drivers_str.strip('[]"')
        if not clean_str:
            return drivers
        
        # Split by '", "' to separate individual driver entries
        driver_entries = re.findall(r'"([^"]+)"', drivers_str)
        
        for entry in driver_entries:
            # Extract driver name and trip count using regex
            # Format: "Driver Name (X trips)"
            match = re.match(r'(.+) \((\d+) trips?\)', entry)
            if match:
                driver_name = match.group(1).strip()
                trip_count = int(match.group(2))
                drivers.append({
                    'name': driver_name,
                    'trips': trip_count
                })
        
        return drivers