import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd
import seaborn as sns
from datetime import datetime, timedelta
from django.conf import settings
from django.db.models import Sum, Count, Q, F
from django.utils.timezone import now, make_aware
from django.core.management.base import BaseCommand
from triplog.models import Trip, TripRoute, Route, Driver, Truck, Product, TripProduct
import numpy as np
from collections import defaultdict
from django.core.mail import EmailMessage

class TripReportGenerator:
    def __init__(self):
        self.report_date = now().date()
        self.start_of_month = now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        self.end_of_month = now()
        
        # Set up matplotlib style
        try:
            plt.style.use('seaborn-v0_8')
        except:
            try:
                plt.style.use('seaborn')
            except:
                plt.style.use('default')
        sns.set_palette("husl")
        
    def generate_comprehensive_report(self):
        """Generate a comprehensive PDF report with all metrics"""
        # Create reports directory if it doesn't exist
        reports_dir = os.path.join(settings.BASE_DIR, 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        
        filename = f"logistics_report_{self.report_date.strftime('%Y_%m_%d')}.pdf"
        filepath = os.path.join(reports_dir, filename)
        
        with PdfPages(filepath) as pdf:
            # Cover page
            self._create_cover_page(pdf)
            
            # Monthly trips per route
            self._create_monthly_trips_per_route(pdf)
            
            # Monthly total kilometres trend
            self._create_monthly_kilometres_trend(pdf)

            # Monthly product distribution
            self._create_monthly_product_distribution(pdf)
            
            # Current ongoing deliveries
            self._create_ongoing_deliveries_summary(pdf)
            
            # Total monthly deliveries trend
            self._create_monthly_deliveries_trend(pdf)
            
            # Driver leaderboard
            self._create_driver_leaderboard(pdf)
            
            # Trip completions per truck company
            self._create_truck_company_performance(pdf)
            
            # Monthly on-time rate trend
            self._create_ontime_rate_trend(pdf)
            
            # Delayed trips list
            self._create_delayed_trips_list(pdf)
            
        return filepath

    def _create_cover_page(self, pdf):
        """Create report cover page"""
        fig, ax = plt.subplots(figsize=(11, 8.5))  # Landscape
        ax.axis('off')
        
        # Title
        ax.text(0.5, 0.8, 'LOGISTICS ANALYTICS REPORT', 
                fontsize=24, fontweight='bold', ha='center', va='center')
        
        # Date
        ax.text(0.5, 0.7, f'Generated on: {self.report_date.strftime("%B %d, %Y")}', 
                fontsize=14, ha='center', va='center')
        
        # Summary stats
        summary_stats = self._get_summary_stats()
        ax.text(0.5, 0.5, 'EXECUTIVE SUMMARY', 
                fontsize=18, fontweight='bold', ha='center', va='center')
        
        summary_text = f"""
Total Trips This Month: {summary_stats['total_monthly_trips']}
Completed Trips: {summary_stats['completed_trips']}
Ongoing Deliveries: {summary_stats['ongoing_deliveries']}
Total Distance Covered: {summary_stats['total_kilometres']:,.0f} km
Average On-Time Rate: {summary_stats['ontime_rate']:.1f}%
Active Drivers: {summary_stats['active_drivers']}
        """
        
        ax.text(0.5, 0.3, summary_text, fontsize=12, ha='center', va='center',
                bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.7))
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()

    def _get_summary_stats(self):
        """Get summary statistics for cover page"""
        total_monthly_trips = Trip.objects.filter(
            departure_time__range=(self.start_of_month, self.end_of_month)
        ).count()
        
        completed_trips = Trip.objects.filter(
            status="Completed",
            departure_time__range=(self.start_of_month, self.end_of_month)
        ).count()
        
        ongoing_deliveries = Trip.objects.filter(status="Ongoing").count()
        
        total_kilometres = TripRoute.objects.filter(
            trip__status="Completed",
            trip__departure_time__range=(self.start_of_month, self.end_of_month)
        ).aggregate(total=Sum('route__distance_km'))['total'] or 0
        
        ontime_trips = TripRoute.objects.filter(
            trip__status="Completed",
            trip__departure_time__range=(self.start_of_month, self.end_of_month),
            actual_time_min__lte=F('route__estimated_time_min')
        ).count()
        
        ontime_rate = (ontime_trips / completed_trips * 100) if completed_trips > 0 else 0
        
        active_drivers = Driver.objects.annotate(
            ongoing_trips=Count('trips', filter=Q(trips__status="Ongoing"))
        ).filter(ongoing_trips=0).count()
        
        return {
            'total_monthly_trips': total_monthly_trips,
            'completed_trips': completed_trips,
            'ongoing_deliveries': ongoing_deliveries,
            'total_kilometres': total_kilometres,
            'ontime_rate': ontime_rate,
            'active_drivers': active_drivers
        }

    def _create_monthly_trips_per_route(self, pdf):
        """Create monthly trips per route chart"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 8.5))  # Landscape
        
        # Get last 6 months of data
        months_data = []
        for i in range(6):
            month_start = (self.start_of_month - timedelta(days=i*30)).replace(day=1)
            if month_start.month == 12:
                month_end = month_start.replace(year=month_start.year + 1, month=1) - timedelta(days=1)
            else:
                month_end = month_start.replace(month=month_start.month + 1) - timedelta(days=1)
            
            month_end = make_aware(datetime.combine(month_end, datetime.max.time()))
            month_start = make_aware(datetime.combine(month_start, datetime.min.time()))
            
            route_data = TripRoute.objects.filter(
                trip__departure_time__range=(month_start, month_end)
            ).values(
                'route__origin', 'route__destination'
            ).annotate(
                trip_count=Count('id')
            ).order_by('-trip_count')[:10]
            
            months_data.append({
                'month': month_start.strftime('%B %Y'),
                'routes': route_data
            })

        # Top routes bar chart for current month
        if months_data[0]['routes']:
            routes = [f"{r['route__origin']} → {r['route__destination']}" for r in months_data[0]['routes']]
            counts = [r['trip_count'] for r in months_data[0]['routes']]
            
            bars = ax1.barh(routes, counts, color=plt.cm.viridis(np.linspace(0, 1, len(routes))))
            ax1.set_title(f'Top 10 Routes - {months_data[0]["month"]}', fontsize=14, fontweight='bold')
            ax1.set_xlabel('Number of Trips')
            
            # Add value labels on bars
            for bar, count in zip(bars, counts):
                ax1.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2, 
                        str(count), va='center', fontweight='bold')
        else:
            ax1.text(0.5, 0.5, 'No route data available', ha='center', va='center', 
                    fontsize=12, transform=ax1.transAxes)
            ax1.set_title('Top Routes - No Data', fontsize=14, fontweight='bold')

        # Route trend over time - Fixed to handle missing data
        # First, collect all unique routes across all months
        all_routes = set()
        for month_data in months_data:
            for route in month_data['routes']:
                route_name = f"{route['route__origin']} → {route['route__destination']}"
                all_routes.add(route_name)

        # Get top 5 routes by total volume across all months
        route_totals = defaultdict(int)
        for month_data in months_data:
            for route in month_data['routes']:
                route_name = f"{route['route__origin']} → {route['route__destination']}"
                route_totals[route_name] += route['trip_count']

        top_routes = sorted(route_totals.items(), key=lambda x: x[1], reverse=True)[:5]

        if top_routes:
            # Prepare month labels (reverse order for chronological display)
            month_labels = [month_data['month'] for month_data in reversed(months_data)]
            
            # For each top route, collect data for all months
            for route_name, _ in top_routes:
                route_counts = []
                
                # For each month (in reverse order), find the count for this route
                for month_data in reversed(months_data):
                    count = 0
                    for route in month_data['routes']:
                        if f"{route['route__origin']} → {route['route__destination']}" == route_name:
                            count = route['trip_count']
                            break
                    route_counts.append(count)
                
                # Now plot the line - both arrays should have same length (6)
                ax2.plot(month_labels, route_counts, marker='o', linewidth=2, 
                        label=route_name, markersize=6)
            
            ax2.set_title('Route Trends Over Last 6 Months', fontsize=14, fontweight='bold')
            ax2.set_xlabel('Month')
            ax2.set_ylabel('Number of Trips')
            ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            ax2.grid(True, alpha=0.3)
            plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
        else:
            ax2.text(0.5, 0.5, 'No trend data available', ha='center', va='center', 
                    fontsize=12, transform=ax2.transAxes)
            ax2.set_title('Route Trends - No Data', fontsize=14, fontweight='bold')

        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()

    def _create_monthly_product_distribution(self, pdf):
        """Create monthly product distribution pie chart"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 8.5))  # Landscape
        
        # Current month product distribution
        product_data = TripProduct.objects.filter(
            trip__departure_time__range=(self.start_of_month, self.end_of_month)
        ).values('product__name').annotate(
            total_quantity=Sum('quantity')
        ).order_by('-total_quantity')
        
        if product_data:
            products = [p['product__name'] for p in product_data]
            quantities = [p['total_quantity'] for p in product_data]
            
            colors = plt.cm.Set3(np.linspace(0, 1, len(products)))
            wedges, texts, autotexts = ax1.pie(quantities, labels=products, autopct='%1.1f%%', 
                                              colors=colors, startangle=90)
            
            ax1.set_title(f'Product Distribution - {self.start_of_month.strftime("%B %Y")}', 
                         fontsize=14, fontweight='bold')
            
            # Make percentage text bold
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
        else:
            ax1.text(0.5, 0.5, 'No product data available', ha='center', va='center', 
                    fontsize=12, transform=ax1.transAxes)
            ax1.set_title('Product Distribution - No Data', fontsize=14, fontweight='bold')
        
        # Product trend over last 6 months - Fixed to handle missing data
        months_product_data = []
        month_labels = []
        
        for i in range(6):
            month_start = (self.start_of_month - timedelta(days=i*30)).replace(day=1)
            if month_start.month == 12:
                month_end = month_start.replace(year=month_start.year + 1, month=1) - timedelta(days=1)
            else:
                month_end = month_start.replace(month=month_start.month + 1) - timedelta(days=1)
            
            month_end = make_aware(datetime.combine(month_end, datetime.max.time()))
            month_start = make_aware(datetime.combine(month_start, datetime.min.time()))
            
            month_products = TripProduct.objects.filter(
                trip__departure_time__range=(month_start, month_end)
            ).values('product__name').annotate(
                total_quantity=Sum('quantity')
            ).order_by('-total_quantity')
            
            months_product_data.append(month_products)
            month_labels.append(month_start.strftime('%b %Y'))
        
        # Create stacked bar chart for product trends
        month_labels.reverse()
        months_product_data.reverse()
        
        # Get all unique products across all months
        all_products = set()
        for month_data in months_product_data:
            all_products.update([p['product__name'] for p in month_data])
        
        if all_products and len(month_labels) > 0:
            try:
                # Prepare data for stacked bar chart - ensure all arrays have same length
                product_monthly_data = {product: [] for product in all_products}
                
                for month_data in months_product_data:
                    month_products = {p['product__name']: p['total_quantity'] for p in month_data}
                    for product in all_products:
                        product_monthly_data[product].append(month_products.get(product, 0))
                
                # Verify all arrays have same length before plotting
                expected_length = len(month_labels)
                valid_products = {}
                for product, quantities in product_monthly_data.items():
                    if len(quantities) == expected_length:
                        valid_products[product] = quantities
                    else:
                        # Pad or trim to correct length
                        if len(quantities) < expected_length:
                            quantities.extend([0] * (expected_length - len(quantities)))
                        else:
                            quantities = quantities[:expected_length]
                        valid_products[product] = quantities
                
                if valid_products:
                    # Create stacked bar chart
                    bottom = np.zeros(len(month_labels))
                    colors = plt.cm.Set3(np.linspace(0, 1, len(valid_products)))
                    
                    for i, (product, quantities) in enumerate(valid_products.items()):
                        ax2.bar(month_labels, quantities, bottom=bottom, label=product, color=colors[i])
                        bottom += np.array(quantities)
                    
                    ax2.set_title('Product Distribution Trends (Last 6 Months)', fontsize=14, fontweight='bold')
                    ax2.set_xlabel('Month')
                    ax2.set_ylabel('Total Quantity')
                    ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
                    ax2.grid(True, alpha=0.3)
                    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
                else:
                    ax2.text(0.5, 0.5, 'No valid product trend data', ha='center', va='center', 
                            fontsize=12, transform=ax2.transAxes)
                    ax2.set_title('Product Trends - No Data', fontsize=14, fontweight='bold')
            except Exception as e:
                ax2.text(0.5, 0.5, f'Error creating product trends\n{str(e)}', ha='center', va='center', 
                        fontsize=12, transform=ax2.transAxes)
                ax2.set_title('Product Trends - Error', fontsize=14, fontweight='bold')
        else:
            ax2.text(0.5, 0.5, 'No product trend data available', ha='center', va='center', 
                    fontsize=12, transform=ax2.transAxes)
            ax2.set_title('Product Trends - No Data', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()

    def _create_ongoing_deliveries_summary(self, pdf):
        """Create ongoing deliveries summary with properly sized table"""
        fig = plt.figure(figsize=(11, 8.5))  # Landscape
        
        # Create main title
        fig.suptitle('ONGOING DELIVERIES SUMMARY', fontsize=20, fontweight='bold', y=0.95)
        
        # Ongoing deliveries count (big number display)
        ax1 = plt.subplot2grid((4, 2), (0, 0), colspan=2)
        ax1.axis('off')
        
        ongoing_trips = Trip.objects.filter(status="Ongoing")
        total_ongoing = ongoing_trips.count()
        
        ax1.text(0.5, 0.5, str(total_ongoing), fontsize=48, fontweight='bold', 
                ha='center', va='center', color='#FF6B35')
        ax1.text(0.5, 0.1, 'ONGOING DELIVERIES', fontsize=16, fontweight='bold', 
                ha='center', va='center')
        
        # Main table showing individual ongoing deliveries
        ax2 = plt.subplot2grid((4, 2), (1, 0), colspan=2, rowspan=3)
        ax2.axis('off')
        
        if total_ongoing > 0:
            # Get individual ongoing deliveries with their details - FIXED APPROACH
            ongoing_deliveries = Trip.objects.filter(status="Ongoing").select_related(
                'driver', 'truck__truck_company'
            )[:15]  # Limit to 15 entries
            
            # Prepare table data
            table_data = []
            headers = ['#', 'Route', 'Driver', 'Company', 'Time']  # Shortened headers
            
            for i, trip in enumerate(ongoing_deliveries, 1):
                # Get the route information using TripRoute model directly
                try:
                    trip_route = TripRoute.objects.filter(trip=trip).select_related('route').first()
                    if trip_route and trip_route.route:
                        route_name = f"{trip_route.route.origin} → {trip_route.route.destination}"
                    else:
                        route_name = "Route not assigned"
                except:
                    route_name = "Route not available"
                
                # Handle case where truck_company might be None
                company_name = trip.truck.truck_company.name if trip.truck.truck_company else "Unknown"
                
                # Format departure time
                departure_str = trip.departure_time.strftime('%m/%d %H:%M') if trip.departure_time else "Not set"
                
                table_data.append([
                    str(i),
                    route_name[:35],  # Truncate long route names
                    trip.driver.name[:20],  # Truncate long names
                    company_name[:20],  # Truncate long company names
                    departure_str
                ])
            
            # Create the table
            if table_data:
                table = ax2.table(cellText=table_data, colLabels=headers, cellLoc='center', loc='center',
                                bbox=[0, 0.1, 1, 0.85])
                
                # Style the table
                table.auto_set_font_size(False)
                table.set_fontsize(9)
                table.scale(1, 1.8)
                
                # Style header
                for i in range(len(headers)):
                    table[(0, i)].set_facecolor('#4ECDC4')
                    table[(0, i)].set_text_props(weight='bold', color='white')
                
                # Alternate row colors
                for i in range(1, len(table_data) + 1):
                    base_color = '#F8F9FA' if i % 2 == 0 else '#FFFFFF'
                    for j in range(len(headers)):
                        table[(i, j)].set_facecolor(base_color)
                
                # Add summary at bottom
                if total_ongoing > 15:
                    ax2.text(0.5, 0.02, f'Showing top 15 of {total_ongoing} ongoing deliveries', 
                            ha='center', va='bottom', transform=ax2.transAxes, 
                            fontsize=10, style='italic')
            else:
                ax2.text(0.5, 0.5, 'No ongoing delivery data available', 
                        ha='center', va='center', fontsize=14, transform=ax2.transAxes)
        else:
            ax2.text(0.5, 0.5, 'No ongoing deliveries found', 
                    ha='center', va='center', fontsize=16, transform=ax2.transAxes)
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()

    def _create_monthly_deliveries_trend(self, pdf):
        """Create monthly deliveries trend - SIMPLIFIED"""
        fig, ax = plt.subplots(1, 1, figsize=(11, 8.5))  # Landscape
        
        # Get last 12 months of data
        months_data = []
        for i in range(12):
            month_start = (self.start_of_month - timedelta(days=i*30)).replace(day=1)
            if month_start.month == 12:
                month_end = month_start.replace(year=month_start.year + 1, month=1) - timedelta(days=1)
            else:
                month_end = month_start.replace(month=month_start.month + 1) - timedelta(days=1)
            
            month_end = make_aware(datetime.combine(month_end, datetime.max.time()))
            month_start = make_aware(datetime.combine(month_start, datetime.min.time()))
            
            completed = Trip.objects.filter(
                status="Completed",
                departure_time__range=(month_start, month_end)
            ).count()
            
            ongoing = Trip.objects.filter(
                status="Ongoing",
                departure_time__range=(month_start, month_end)
            ).count()
            
            total = completed + ongoing
            
            months_data.append({
                'month': month_start.strftime('%b %Y'),
                'completed': completed,
                'ongoing': ongoing,
                'total': total
            })

        months_data.reverse()
        
        # Extract data for plotting
        months = [m['month'] for m in months_data]
        completed = [m['completed'] for m in months_data]
        ongoing = [m['ongoing'] for m in months_data]
        total = [m['total'] for m in months_data]
        
        # Total deliveries trend
        ax.plot(months, total, marker='o', linewidth=3, markersize=8, color='blue', label='Total Deliveries')
        ax.plot(months, completed, marker='s', linewidth=2, markersize=6, color='green', label='Completed')
        ax.plot(months, ongoing, marker='^', linewidth=2, markersize=6, color='orange', label='Ongoing')
        
        ax.set_title('Monthly Deliveries Trend (Last 12 Months)', fontsize=16, fontweight='bold')
        ax.set_xlabel('Month')
        ax.set_ylabel('Number of Deliveries')
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()

    def _create_driver_leaderboard(self, pdf):
        """Create driver leaderboard charts - SIMPLIFIED"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 8.5))  # Landscape
        
        # Monthly driver performance
        monthly_drivers = Trip.objects.filter(
            status="Completed",
            departure_time__range=(self.start_of_month, self.end_of_month)
        ).values('driver__name').annotate(
            trips=Count('id')
        ).order_by('-trips')[:10]
        
        if monthly_drivers:
            drivers = [d['driver__name'] for d in monthly_drivers]
            trips = [d['trips'] for d in monthly_drivers]
            
            bars = ax1.barh(drivers, trips, color=plt.cm.viridis(np.linspace(0, 1, len(drivers))))
            ax1.set_title(f'Top Drivers - {self.start_of_month.strftime("%B %Y")}', 
                         fontsize=14, fontweight='bold')
            ax1.set_xlabel('Number of Completed Trips')
            
            for bar, trip_count in zip(bars, trips):
                ax1.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2, 
                        str(trip_count), va='center', fontweight='bold')
        else:
            ax1.text(0.5, 0.5, 'No driver data available', ha='center', va='center', 
                    fontsize=12, transform=ax1.transAxes)
            ax1.set_title('Monthly Top Drivers - No Data', fontsize=14, fontweight='bold')

        # Overall driver performance (last 6 months)
        six_months_ago = self.start_of_month - timedelta(days=180)
        overall_drivers = Trip.objects.filter(
            status="Completed",
            departure_time__gte=six_months_ago
        ).values('driver__name').annotate(
            trips=Count('id')
        ).order_by('-trips')[:10]
        
        if overall_drivers:
            drivers = [d['driver__name'] for d in overall_drivers]
            trips = [d['trips'] for d in overall_drivers]
            
            bars = ax2.bar(range(len(drivers)), trips, color='lightblue')
            ax2.set_title('Overall Top Drivers (Last 6 Months)', fontsize=14, fontweight='bold')
            ax2.set_ylabel('Number of Completed Trips')
            ax2.set_xticks(range(len(drivers)))
            ax2.set_xticklabels(drivers, rotation=45, ha='right')
            
            for bar, trip_count in zip(bars, trips):
                ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                        str(trip_count), ha='center', va='bottom', fontweight='bold')
        else:
            ax2.text(0.5, 0.5, 'No overall driver data available', ha='center', va='center', 
                    fontsize=12, transform=ax2.transAxes)
            ax2.set_title('Overall Top Drivers - No Data', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()

    def _create_truck_company_performance(self, pdf):
        """Create truck company performance charts with ACTUAL DATA"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 8.5))  # Landscape
        
        # Monthly truck company performance
        monthly_companies = Trip.objects.filter(
            status="Completed",
            departure_time__range=(self.start_of_month, self.end_of_month)
        ).values('truck__truck_company__name').annotate(
            trips=Count('id')
        ).order_by('-trips')
        
        if monthly_companies:
            companies = [c['truck__truck_company__name'] for c in monthly_companies]
            trips = [c['trips'] for c in monthly_companies]
            
            colors = plt.cm.Set3(np.linspace(0, 1, len(companies)))
            wedges, texts, autotexts = ax1.pie(trips, labels=companies, autopct='%1.1f%%', 
                                              colors=colors, startangle=90)
            ax1.set_title(f'Monthly Trip Completions by Company - {self.start_of_month.strftime("%B %Y")}', 
                         fontsize=14, fontweight='bold')
            
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
        else:
            ax1.text(0.5, 0.5, 'No monthly company data available', ha='center', va='center', 
                    fontsize=12, transform=ax1.transAxes)
            ax1.set_title('Monthly Company Performance - No Data', fontsize=14, fontweight='bold')

        # Overall company performance (last 6 months)
        six_months_ago = self.start_of_month - timedelta(days=180)
        overall_companies = Trip.objects.filter(
            status="Completed",
            departure_time__gte=six_months_ago
        ).values('truck__truck_company__name').annotate(
            trips=Count('id')
        ).order_by('-trips')
        
        if overall_companies:
            companies = [c['truck__truck_company__name'] for c in overall_companies]
            trips = [c['trips'] for c in overall_companies]
            
            bars = ax2.bar(companies, trips, color='lightgreen')
            ax2.set_title('Overall Company Performance (Last 6 Months)', 
                         fontsize=14, fontweight='bold')
            ax2.set_ylabel('Number of Completed Trips')
            ax2.set_xlabel('Company')
            plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
            
            for bar, trip_count in zip(bars, trips):
                ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                        str(trip_count), ha='center', va='bottom', fontweight='bold')
        else:
            ax2.text(0.5, 0.5, 'No overall company data available', ha='center', va='center', 
                    fontsize=12, transform=ax2.transAxes)
            ax2.set_title('Overall Company Performance - No Data', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()

    def _create_ontime_rate_trend(self, pdf):
        """Create monthly on-time rate trend chart with ACTUAL DATA"""
        fig, ax = plt.subplots(1, 1, figsize=(11, 8.5))  # Landscape
        
        # Monthly on-time rate trend
        ontime_data = []
        month_labels = []
        
        for i in range(12):
            month_start = (self.start_of_month - timedelta(days=i*30)).replace(day=1)
            if month_start.month == 12:
                month_end = month_start.replace(year=month_start.year + 1, month=1) - timedelta(days=1)
            else:
                month_end = month_start.replace(month=month_start.month + 1) - timedelta(days=1)
            
            month_end = make_aware(datetime.combine(month_end, datetime.max.time()))
            month_start = make_aware(datetime.combine(month_start, datetime.min.time()))
            
            total_completed = TripRoute.objects.filter(
                trip__status="Completed",
                trip__departure_time__range=(month_start, month_end),
                actual_time_min__isnull=False
            ).count()
            
            ontime_completed = TripRoute.objects.filter(
                trip__status="Completed",
                trip__departure_time__range=(month_start, month_end),
                actual_time_min__lte=F('route__estimated_time_min')
            ).count()
            
            ontime_rate = (ontime_completed / total_completed * 100) if total_completed > 0 else 0
            
            ontime_data.append(ontime_rate)
            month_labels.append(month_start.strftime('%b %Y'))

        ontime_data.reverse()
        month_labels.reverse()
        
        if any(rate > 0 for rate in ontime_data):
            # Plot on-time rate trend
            ax.plot(month_labels, ontime_data, marker='o', linewidth=3, markersize=8, color='blue')
            ax.fill_between(month_labels, ontime_data, alpha=0.3, color='blue')
            ax.set_title('Monthly On-Time Rate Trend (Last 12 Months)', 
                         fontsize=16, fontweight='bold')
            ax.set_xlabel('Month')
            ax.set_ylabel('On-Time Rate (%)')
            ax.set_ylim(0, 100)
            ax.grid(True, alpha=0.3)
            ax.axhline(y=80, color='green', linestyle='--', alpha=0.7, label='Target (80%)')
            ax.legend()
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
            
            # Add value labels
            for i, rate in enumerate(ontime_data):
                if rate > 0:  # Only show labels for non-zero values
                    ax.text(i, rate + 2, f'{rate:.1f}%', ha='center', va='bottom', fontweight='bold')
        else:
            ax.text(0.5, 0.5, 'No on-time rate data available', ha='center', va='center', 
                    fontsize=16, transform=ax.transAxes)
            ax.set_title('Monthly On-Time Rate Trend - No Data', fontsize=16, fontweight='bold')
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()

    def _create_monthly_kilometres_trend(self, pdf):
        """Create monthly kilometres trend chart with ACTUAL DATA"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 8.5))  # Landscape
        
        # Monthly kilometres trend
        km_data = []
        month_labels = []
        
        for i in range(12):
            month_start = (self.start_of_month - timedelta(days=i*30)).replace(day=1)
            if month_start.month == 12:
                month_end = month_start.replace(year=month_start.year + 1, month=1) - timedelta(days=1)
            else:
                month_end = month_start.replace(month=month_start.month + 1) - timedelta(days=1)
            
            month_end = make_aware(datetime.combine(month_end, datetime.max.time()))
            month_start = make_aware(datetime.combine(month_start, datetime.min.time()))
            
            total_km = TripRoute.objects.filter(
                trip__status="Completed",
                trip__departure_time__range=(month_start, month_end)
            ).aggregate(total=Sum('route__distance_km'))['total'] or 0
            
            km_data.append(total_km)
            month_labels.append(month_start.strftime('%b %Y'))

        km_data.reverse()
        month_labels.reverse()
        
        # Plot total kilometres trend
        if any(km > 0 for km in km_data):
            ax1.plot(month_labels, km_data, marker='o', linewidth=3, markersize=8, color='green')
            ax1.fill_between(month_labels, km_data, alpha=0.3, color='green')
            ax1.set_title('Monthly Total Kilometres Trend (Last 12 Months)', 
                         fontsize=16, fontweight='bold')
            ax1.set_xlabel('Month')
            ax1.set_ylabel('Total Kilometres')
            ax1.grid(True, alpha=0.3)
            plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
            
            # Add value labels for non-zero values
            for i, km in enumerate(km_data):
                if km > 0:
                    ax1.text(i, km + max(km_data) * 0.02, f'{km:,.0f}', ha='center', va='bottom', fontweight='bold')
        else:
            ax1.text(0.5, 0.5, 'No kilometres data available', ha='center', va='center', 
                    fontsize=12, transform=ax1.transAxes)
            ax1.set_title('Monthly Kilometres Trend - No Data', fontsize=16, fontweight='bold')
        
        # Kilometres by route category
        route_km_data = TripRoute.objects.filter(
            trip__status="Completed",
            trip__departure_time__range=(self.start_of_month, self.end_of_month)
        ).values(
            'route__origin', 'route__destination'
        ).annotate(
            total_km=Sum('route__distance_km'),
            trip_count=Count('id')
        ).order_by('-total_km')[:10]
        
        if route_km_data:
            routes = [f"{r['route__origin']} → {r['route__destination']}" for r in route_km_data]
            total_kms = [r['total_km'] for r in route_km_data]
            
            bars = ax2.barh(routes, total_kms, color=plt.cm.plasma(np.linspace(0, 1, len(routes))))
            ax2.set_title(f'Top Routes by Total Kilometres - {self.start_of_month.strftime("%B %Y")}', 
                         fontsize=16, fontweight='bold')
            ax2.set_xlabel('Total Kilometres')
            
            for bar, km in zip(bars, total_kms):
                ax2.text(bar.get_width() + max(total_kms) * 0.01, 
                        bar.get_y() + bar.get_height()/2, 
                        f'{km:,.0f}', va='center', fontweight='bold')
        else:
            ax2.text(0.5, 0.5, 'No route kilometre data available', ha='center', va='center', 
                    fontsize=12, transform=ax2.transAxes)
            ax2.set_title('Top Routes by Kilometres - No Data', fontsize=16, fontweight='bold')
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()

    def _create_delayed_trips_list(self, pdf):
        """Create reasonably sized delayed trips table"""
        fig = plt.figure(figsize=(11, 8.5))  # Landscape
        ax = fig.add_subplot(111)
        ax.axis('off')
        
        # Create title
        ax.text(0.5, 0.95, 'DELAYED TRIPS REPORT', fontsize=18, fontweight='bold', 
                ha='center', va='top', transform=ax.transAxes)
        ax.text(0.5, 0.92, f'{self.start_of_month.strftime("%B %Y")} - Most Delayed Trips', 
                fontsize=12, ha='center', va='top', transform=ax.transAxes)
        
        # Get delayed trips
        delayed_trips = TripRoute.objects.filter(
            trip__status="Completed",
            trip__departure_time__range=(self.start_of_month, self.end_of_month),
            actual_time_min__gt=F('route__estimated_time_min')
        ).select_related('trip__driver', 'trip__truck__truck_company', 'route').order_by('-actual_time_min')[:12]
        
        def format_time(minutes):
            """Convert minutes to hours and minutes format"""
            if minutes < 60:
                return f"{minutes}min"
            hours = minutes // 60
            mins = minutes % 60
            if mins == 0:
                return f"{hours}h"
            return f"{hours}h {mins}min"
        
        if delayed_trips:
            # Prepare table data
            table_data = []
            headers = ['#', 'Route', 'Driver', 'Company', 'Est', 'Actual', 'Delay']  # Shortened headers
            
            for i, trip_route in enumerate(delayed_trips, 1):
                delay_min = trip_route.actual_time_min - trip_route.route.estimated_time_min
                
                # Handle case where truck_company might be None
                company_name = trip_route.trip.truck.truck_company.name if trip_route.trip.truck.truck_company else "Unknown"
                
                table_data.append([
                    str(i),
                    f"{trip_route.route.origin} → {trip_route.route.destination}"[:25],
                    trip_route.trip.driver.name[:15],
                    company_name[:15],
                    format_time(trip_route.route.estimated_time_min),
                    format_time(trip_route.actual_time_min),
                    format_time(delay_min)
                ])

            # Create table
            table = ax.table(cellText=table_data, colLabels=headers, cellLoc='center', loc='center',
                           bbox=[0, 0.25, 1, 0.65])
            
            # Style the table
            table.auto_set_font_size(False)
            table.set_fontsize(9)
            table.scale(1, 1.8)
            
            # Style header
            for i in range(len(headers)):
                table[(0, i)].set_facecolor('#FF6B6B')
                table[(0, i)].set_text_props(weight='bold', color='white')
            
            # Alternate row colors for better readability
            for i in range(1, len(table_data) + 1):
                color = '#F8F9FA' if i % 2 == 0 else '#FFFFFF'
                for j in range(len(headers)):
                    table[(i, j)].set_facecolor(color)

            # Summary statistics
            total_delayed = len(delayed_trips)
            avg_delay = sum(trip_route.actual_time_min - trip_route.route.estimated_time_min 
                           for trip_route in delayed_trips) / total_delayed if total_delayed > 0 else 0
            max_delay = max(trip_route.actual_time_min - trip_route.route.estimated_time_min 
                           for trip_route in delayed_trips) if delayed_trips else 0
            
            # Get total delayed trips count for the month
            total_delayed_month = TripRoute.objects.filter(
                trip__status="Completed",
                trip__departure_time__range=(self.start_of_month, self.end_of_month),
                actual_time_min__gt=F('route__estimated_time_min')
            ).count()
            
            summary_text = f"""SUMMARY STATISTICS:
• Total Delayed Trips This Month: {total_delayed_month}
• Average Delay: {format_time(int(avg_delay))}
• Maximum Delay: {format_time(max_delay)}
• Showing: Top {total_delayed} most delayed trips"""
            
            ax.text(0.5, 0.15, summary_text, fontsize=11, ha='center', va='top', 
                   transform=ax.transAxes, fontweight='bold',
                   bbox=dict(boxstyle="round,pad=0.5", facecolor="#FFE5E5", alpha=0.8))
        else:
            ax.text(0.5, 0.5, 'No delayed trips found for this period', 
                   fontsize=16, ha='center', va='center', transform=ax.transAxes)
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()

    def send_monthly_report_email(self, filepath, recipients=None):
        """Send the generated report via email"""
        if recipients is None:
            recipients = getattr(settings, 'MONTHLY_REPORT_RECIPIENTS', [])
        
        if not recipients:
            raise ValueError("No email recipients configured")
        
        print("=" * 50)
        print("SENDING EMAIL VIA CONSOLE BACKEND")
        print("=" * 50)
        
        subject = f'Monthly Logistics Report - {self.report_date.strftime("%B %Y")}'
        
        body = f"""
Dear Team,

Please find attached the monthly Logistics Analytics report for {self.report_date.strftime("%B %Y")}.

This report includes:
• Route performance analysis
• Driver performance metrics
• Company performance statistics
• On-time delivery trends
• Delayed trips analysis
• Product distribution insights

Best regards,
Logistics Analytics System

This is an automatically generated email. Please do not reply to this email as the email address is not monitored.
        """
        
        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@company.com'),
            to=recipients,
        )
        
        # Attach the PDF file
        with open(filepath, 'rb') as f:
            email.attach(
                f'logistics_report_{self.report_date.strftime("%Y_%m_%d")}.pdf',
                f.read(),
                'application/pdf'
            )
        
        # This will output to the runserver console
        email.send()
        
        print("=" * 50)
        print("EMAIL SENT TO CONSOLE")
        print("=" * 50)
        
        return True

# Django management command
class Command(BaseCommand):
    help = 'Generate comprehensive trip analytics PDF report'
    
    def handle(self, *args, **options):
        try:
            generator = TripReportGenerator()
            filepath = generator.generate_comprehensive_report()
            
            self.stdout.write(
                self.style.SUCCESS(f'Report generated successfully: {filepath}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error generating report: {str(e)}')
            )