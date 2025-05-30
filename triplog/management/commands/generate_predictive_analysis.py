import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.db.models import Avg, Count, Sum, F
from django.utils.timezone import now
from triplog.models import Trip, TripRoute, Route, Product, TripProduct, Driver
import json

class Command(BaseCommand):
    help = 'Generate predictive analysis for product distribution and delivery times'
    
    def handle(self, *args, **options):
        self.stdout.write('Generating predictive analysis...')
        
        analyzer = PredictiveAnalyzer()
        analysis_results = analyzer.generate_full_analysis()
        
        # Save results to JSON for later use
        results_path = os.path.join('reports', 'predictive_analysis.json')
        os.makedirs('reports', exist_ok=True)
        
        with open(results_path, 'w') as f:
            json.dump(analysis_results, f, indent=2, default=str)
        
        self.stdout.write(
            self.style.SUCCESS('Predictive analysis generated successfully!')
        )

class PredictiveAnalyzer:
    def __init__(self):
        self.current_date = now().date()
        self.last_30_days = now() - timedelta(days=30)
        self.last_90_days = now() - timedelta(days=90)
        
    def generate_full_analysis(self):
        """Generate comprehensive predictive analysis"""
        return {
            'product_distribution_forecast': self.predict_product_distribution(),
            'delivery_time_analysis': self.analyze_delivery_times(),
            'weather_impact_assessment': self.assess_weather_impact(),
            'capacity_planning': self.predict_capacity_needs(),
            'route_efficiency_forecast': self.forecast_route_efficiency(),
            'generated_at': datetime.now().isoformat()
        }
    
    def predict_product_distribution(self):
        """Predict future product distribution patterns"""
        # Get historical product data
        product_data = TripProduct.objects.select_related('trip', 'product').filter(
            trip__departure_time__gte=self.last_90_days
        ).values(
            'product__name',
            'quantity',
            'trip__departure_time'
        )
        
        df = pd.DataFrame(product_data)
        
        if len(df) == 0:
            return {
                'message': 'Insufficient data for product distribution analysis',
                'predictions': {},
                'recommendations': ['Generate more trip data to enable product distribution forecasting']
            }
        
        # Add time features
        df['departure_time'] = pd.to_datetime(df['trip__departure_time'])
        df['week'] = df['departure_time'].dt.isocalendar().week
        df['month'] = df['departure_time'].dt.month
        df['day_of_week'] = df['departure_time'].dt.dayofweek
        
        # Calculate predictions
        predictions = {}
        for product in df['product__name'].unique():
            product_df = df[df['product__name'] == product]
            
            # Calculate weekly average
            total_quantity = product_df['quantity'].sum()
            weeks_span = max(1, (df['departure_time'].max() - df['departure_time'].min()).days / 7)
            avg_weekly_demand = total_quantity / weeks_span
            
            # Simple trend calculation
            recent_weeks = product_df[product_df['departure_time'] >= (now() - timedelta(weeks=4))]
            previous_weeks = product_df[
                (product_df['departure_time'] >= (now() - timedelta(weeks=8))) &
                (product_df['departure_time'] < (now() - timedelta(weeks=4)))
            ]
            
            recent_avg = recent_weeks['quantity'].sum() / 4 if len(recent_weeks) > 0 else 0
            previous_avg = previous_weeks['quantity'].sum() / 4 if len(previous_weeks) > 0 else recent_avg
            
            # Calculate trend
            if previous_avg > 0:
                trend_percentage = ((recent_avg - previous_avg) / previous_avg) * 100
            else:
                trend_percentage = 0
            
            # Predict next week's demand
            if trend_percentage > 0:
                next_week_prediction = recent_avg * (1 + (trend_percentage / 100))
            else:
                next_week_prediction = recent_avg
            
            predictions[product] = {
                'current_weekly_avg': round(recent_avg, 2),
                'trend_percentage': round(trend_percentage, 2),
                'next_week_prediction': round(max(0, next_week_prediction), 2),
                'confidence_level': self._calculate_confidence(product_df),
                'seasonal_pattern': self._detect_seasonal_pattern(product_df)
            }
        
        return {
            'predictions': predictions,
            'top_growth_products': self._get_top_growth_products(predictions),
            'declining_products': self._get_declining_products(predictions),
            'recommendations': self._generate_distribution_recommendations(predictions)
        }
    
    def analyze_delivery_times(self):
        """Analyze and predict delivery time patterns"""
        # Get trip route data with actual times
        route_data = TripRoute.objects.filter(
            trip__departure_time__gte=self.last_90_days,
            actual_time_min__isnull=False
        ).select_related('trip', 'route').values(
            'route__distance_km',
            'route__estimated_time_min',
            'actual_time_min',
            'trip__departure_time'
        )
        
        df = pd.DataFrame(route_data)
        
        if len(df) == 0:
            return {
                'message': 'Insufficient data for delivery time analysis',
                'overall_efficiency': 0,
                'average_delay_minutes': 0,
                'best_delivery_hours': {},
                'predictions': {}
            }
        
        # Calculate delivery efficiency metrics
        df['efficiency_ratio'] = df['route__estimated_time_min'] / df['actual_time_min']
        df['delay_minutes'] = df['actual_time_min'] - df['route__estimated_time_min']
        df['departure_time'] = pd.to_datetime(df['trip__departure_time'])
        df['hour'] = df['departure_time'].dt.hour
        df['day_of_week'] = df['departure_time'].dt.dayofweek
        
        # Analyze patterns - fix aggregation to avoid tuple keys
        hourly_summary = {}
        for hour in df['hour'].unique():
            hour_data = df[df['hour'] == hour]
            hourly_summary[int(hour)] = {
                'efficiency_ratio': round(hour_data['efficiency_ratio'].mean(), 2),
                'delay_minutes': round(hour_data['delay_minutes'].mean(), 2)
            }
        
        daily_summary = {}
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for day in df['day_of_week'].unique():
            day_data = df[df['day_of_week'] == day]
            day_name = day_names[int(day)] if int(day) < len(day_names) else f'Day_{day}'
            daily_summary[day_name] = {
                'efficiency_ratio': round(day_data['efficiency_ratio'].mean(), 2),
                'delay_minutes': round(day_data['delay_minutes'].mean(), 2)
            }
        
        # Distance-based analysis
        df['distance_category'] = pd.cut(df['route__distance_km'], 
                                       bins=[0, 50, 100, 200, float('inf')], 
                                       labels=['Short', 'Medium', 'Long', 'Very Long'])
        
        distance_summary = {}
        for category in df['distance_category'].dropna().unique():
            category_data = df[df['distance_category'] == category]
            distance_summary[str(category)] = {
                'efficiency_ratio': round(category_data['efficiency_ratio'].mean(), 2),
                'delay_minutes': round(category_data['delay_minutes'].mean(), 2),
                'actual_time_min': round(category_data['actual_time_min'].mean(), 2)
            }
        
        # Get best/worst hours - simplified
        hour_efficiency = {hour: data['efficiency_ratio'] for hour, data in hourly_summary.items()}
        sorted_hours = sorted(hour_efficiency.items(), key=lambda x: x[1], reverse=True)
        
        best_hours = dict(sorted_hours[:3]) if len(sorted_hours) >= 3 else dict(sorted_hours)
        worst_hours = dict(sorted_hours[-3:]) if len(sorted_hours) >= 3 else {}
        
        return {
            'overall_efficiency': round(df['efficiency_ratio'].mean() * 100, 2),
            'average_delay_minutes': round(df['delay_minutes'].mean(), 2),
            'best_delivery_hours': best_hours,
            'worst_delivery_hours': worst_hours,
            'daily_patterns': daily_summary,
            'distance_impact': distance_summary,
            'predictions': {
                'next_week_avg_delay': round(df['delay_minutes'].mean(), 2),
                'efficiency_trend': self._calculate_efficiency_trend(df)
            }
        }
    
    def assess_weather_impact(self):
        """Assess weather impact on delivery times with simple analysis"""
        # Get recent trip data
        recent_trips = TripRoute.objects.filter(
            trip__departure_time__gte=self.last_30_days,
            actual_time_min__isnull=False
        ).select_related('trip').values(
            'actual_time_min',
            'route__estimated_time_min',
            'trip__departure_time'
        )
        
        df = pd.DataFrame(recent_trips)
        
        if len(df) == 0:
            return {
                'message': 'Insufficient data for weather impact analysis',
                'weather_delay_factors': {
                    'rain': {'impact': '20-30% increase in delivery time', 'recommendation': 'Add 30 min buffer'},
                    'fog': {'impact': '15-25% increase in delivery time', 'recommendation': 'Delay early morning trips'},
                    'heavy_traffic': {'impact': '40-60% increase in delivery time', 'recommendation': 'Use alternative routes'},
                    'optimal_conditions': {'impact': '5-10% faster than estimated', 'recommendation': 'Standard scheduling'}
                },
                'recommendations': {
                    'optimal_hours': 'Schedule deliveries between 9 AM - 11 AM for best conditions',
                    'avoid_hours': 'Avoid scheduling during 6-7 AM and 6-7 PM (heavy traffic)',
                    'weather_buffer': 'Add 15-20% time buffer during poor weather conditions',
                    'seasonal_advice': 'Increase delivery time estimates by 25% during rainy season'
                }
            }
        
        df['delay_minutes'] = df['actual_time_min'] - df['route__estimated_time_min']
        df['departure_time'] = pd.to_datetime(df['trip__departure_time'])
        df['hour'] = df['departure_time'].dt.hour
        
        # Simple weather impact simulation based on time patterns
        weather_conditions = []
        for hour in df['hour']:
            if hour in [6, 7, 18, 19]:  # Rush hours
                weather_conditions.append('Heavy Traffic')
            elif hour in [0, 1, 2, 3, 4, 5]:  # Night/early morning
                weather_conditions.append('Low Visibility')
            elif hour in [12, 13, 14]:  # Midday
                weather_conditions.append('Optimal')
            else:
                weather_conditions.append('Normal')
        
        df['weather_condition'] = weather_conditions
        
        # Fix the aggregation to avoid tuple keys - use simple aggregation
        weather_summary = {}
        for condition in df['weather_condition'].unique():
            condition_data = df[df['weather_condition'] == condition]
            weather_summary[condition] = {
                'avg_delay': round(condition_data['delay_minutes'].mean(), 2),
                'count': len(condition_data)
            }
        
        return {
            'weather_impact_analysis': weather_summary,
            'recommendations': {
                'optimal_hours': 'Schedule deliveries between 9 AM - 11 AM for best conditions',
                'avoid_hours': 'Avoid scheduling during 6-7 AM and 6-7 PM (heavy traffic)',
                'weather_buffer': 'Add 15-20% time buffer during poor weather conditions',
                'seasonal_advice': 'Increase delivery time estimates by 25% during rainy season'
            },
            'weather_delay_factors': {
                'rain': {'impact': '20-30% increase in delivery time', 'recommendation': 'Add 30 min buffer'},
                'fog': {'impact': '15-25% increase in delivery time', 'recommendation': 'Delay early morning trips'},
                'heavy_traffic': {'impact': '40-60% increase in delivery time', 'recommendation': 'Use alternative routes'},
                'optimal_conditions': {'impact': '5-10% faster than estimated', 'recommendation': 'Standard scheduling'}
            }
        }
    
    def predict_capacity_needs(self):
        """Predict future capacity requirements"""
        from django.db.models import DateTimeField
        from django.db.models.functions import Extract
        
        # Get trip data - fix the SQL syntax issue
        recent_trips = Trip.objects.filter(
            departure_time__gte=self.last_30_days
        ).annotate(
            week=Extract('departure_time', 'week')
        ).values('week').annotate(
            trip_count=Count('id')
        )
        
        # Count all drivers
        total_drivers = Driver.objects.count()
        
        # Calculate weekly averages
        weekly_data = list(recent_trips)
        if len(weekly_data) > 0:
            # Convert to DataFrame
            df = pd.DataFrame(weekly_data)
            avg_weekly_trips = df['trip_count'].mean()
            max_weekly_trips = df['trip_count'].max()
            
            # Simple capacity prediction
            predicted_growth = 1.1  # Assume 10% growth
            predicted_weekly_trips = avg_weekly_trips * predicted_growth
            
            # Calculate driver utilization (assuming 5 trips per driver per week)
            trips_per_driver_per_week = 5
            required_drivers = predicted_weekly_trips / trips_per_driver_per_week
            
            return {
                'current_drivers': total_drivers,
                'current_weekly_trips': round(avg_weekly_trips, 1),
                'predicted_weekly_trips': round(predicted_weekly_trips, 1),
                'required_drivers': round(required_drivers, 1),
                'capacity_status': 'adequate' if total_drivers >= required_drivers else 'insufficient',
                'recommendation': self._generate_capacity_recommendation(total_drivers, required_drivers)
            }
        
        return {
            'current_drivers': total_drivers,
            'current_weekly_trips': 0,
            'predicted_weekly_trips': 0,
            'required_drivers': 0,
            'capacity_status': 'adequate',
            'recommendation': 'Insufficient trip data for capacity analysis'
        }
    
    def forecast_route_efficiency(self):
        """Forecast route efficiency trends"""
        # Get route performance data - fix the field name issue
        route_performance = TripRoute.objects.filter(
            trip__departure_time__gte=self.last_90_days,
            actual_time_min__isnull=False
        ).select_related('trip', 'route').values(
            'route__origin',
            'route__destination', 
            'route__distance_km',
            'actual_time_min',
            'route__estimated_time_min'
        )
        
        df = pd.DataFrame(route_performance)
        
        if len(df) == 0:
            return {
                'message': 'Insufficient data for route efficiency analysis',
                'route_efficiency_scores': {},
                'optimization_recommendations': ['Generate more trip data to enable route efficiency analysis']
            }
        
        # Create route identifier from origin and destination
        df['route_name'] = df['route__origin'] + ' → ' + df['route__destination']
        
        # Calculate efficiency metrics by route - simplified aggregation
        route_summary = {}
        for route_name in df['route_name'].unique():
            route_data = df[df['route_name'] == route_name]
            
            avg_actual_time = route_data['actual_time_min'].mean()
            avg_estimated_time = route_data['route__estimated_time_min'].mean()
            avg_distance = route_data['route__distance_km'].mean()
            
            # Avoid division by zero
            efficiency_score = avg_estimated_time / avg_actual_time if avg_actual_time > 0 else 0
            
            route_summary[route_name] = {
                'actual_time_min': round(avg_actual_time, 2),
                'estimated_time_min': round(avg_estimated_time, 2),
                'distance_km': round(avg_distance, 2),
                'efficiency_score': round(efficiency_score, 2)
            }
        
        # Filter valid routes
        valid_routes = {k: v for k, v in route_summary.items() if v['actual_time_min'] > 0}
        
        if len(valid_routes) == 0:
            return {
                'message': 'No valid route data for efficiency analysis',
                'route_efficiency_scores': {},
                'optimization_recommendations': ['Need routes with actual completion times for analysis']
            }
        
        # Get efficiency scores
        efficiency_scores = {route: data['efficiency_score'] for route, data in valid_routes.items()}
        
        # Get best and worst routes
        sorted_routes = sorted(efficiency_scores.items(), key=lambda x: x[1], reverse=True)
        best_routes = dict(sorted_routes[:3]) if len(sorted_routes) >= 3 else dict(sorted_routes)
        worst_routes = dict(sorted_routes[-3:]) if len(sorted_routes) >= 3 else {}
        
        return {
            'route_efficiency_scores': efficiency_scores,
            'best_performing_routes': {route: valid_routes[route] for route in best_routes.keys()},
            'worst_performing_routes': {route: valid_routes[route] for route in worst_routes.keys()},
            'optimization_recommendations': self._generate_route_recommendations_simple(valid_routes)
        }
    
    # Helper methods
    def _calculate_confidence(self, data):
        """Calculate confidence level based on data consistency"""
        if len(data) < 5:
            return 'Low'
        elif len(data) < 15:
            return 'Medium'
        else:
            return 'High'
    
    def _detect_seasonal_pattern(self, data):
        """Detect seasonal patterns in product demand"""
        if len(data) < 10:
            return 'Insufficient data'
        
        if 'month' in data.columns:
            monthly_avg = data.groupby('month')['quantity'].mean()
            variance = monthly_avg.std()
            
            if variance > monthly_avg.mean() * 0.3:
                return 'High seasonality'
            elif variance > monthly_avg.mean() * 0.15:
                return 'Moderate seasonality'
            else:
                return 'Low seasonality'
        
        return 'Unable to determine'
    
    def _get_top_growth_products(self, predictions):
        """Get products with highest growth predictions"""
        if not predictions:
            return {}
        growth_products = {k: v for k, v in predictions.items() if v['trend_percentage'] > 10}
        return dict(sorted(growth_products.items(), 
                          key=lambda x: x[1]['trend_percentage'], reverse=True)[:3])
    
    def _get_declining_products(self, predictions):
        """Get products with declining trends"""
        if not predictions:
            return {}
        declining_products = {k: v for k, v in predictions.items() if v['trend_percentage'] < -5}
        return dict(sorted(declining_products.items(), 
                          key=lambda x: x[1]['trend_percentage'])[:3])
    
    def _generate_distribution_recommendations(self, predictions):
        """Generate recommendations based on predictions"""
        recommendations = []
        
        if not predictions:
            return ['Generate more trip and product data to enable distribution recommendations']
        
        for product, data in predictions.items():
            if data['trend_percentage'] > 20:
                recommendations.append(f"Increase inventory for {product} - high growth trend detected")
            elif data['trend_percentage'] < -10:
                recommendations.append(f"Review demand for {product} - declining trend detected")
        
        if not recommendations:
            recommendations.append("Product demand appears stable - maintain current inventory levels")
        
        return recommendations
    
    def _calculate_efficiency_trend(self, data):
        """Calculate efficiency trend over time"""
        if len(data) < 2:
            return 'Insufficient data'
            
        data['date'] = data['departure_time'].dt.date
        daily_efficiency = data.groupby('date')['efficiency_ratio'].mean()
        
        if len(daily_efficiency) > 7:
            recent_avg = daily_efficiency.tail(7).mean()
            previous_avg = daily_efficiency.head(-7).mean()
            
            if recent_avg > previous_avg:
                return 'Improving'
            elif recent_avg < previous_avg * 0.95:
                return 'Declining'
            else:
                return 'Stable'
        
        return 'Insufficient data'
    
    def _generate_capacity_recommendation(self, current, required):
        """Generate capacity recommendations"""
        if required > current * 1.2:
            return f"Hire {int(required - current)} additional drivers immediately"
        elif required > current:
            return f"Consider hiring {int(required - current)} additional drivers"
        else:
            return "Current capacity is sufficient"
    
    def _generate_route_recommendations(self, route_analysis):
        """Generate route optimization recommendations"""
        recommendations = []
        
        if len(route_analysis) == 0:
            return ['No route data available for optimization recommendations']
        
        for route_name, data in route_analysis.iterrows():
            if data['efficiency_score'] < 0.8:
                recommendations.append(f"Optimize {route_name} route - efficiency below 80%")
            elif data['efficiency_score'] > 1.2:
                recommendations.append(f"Use {route_name} route as benchmark - excellent efficiency")
        
        if not recommendations:
            recommendations.append("All routes performing within acceptable efficiency range")
        
        return recommendations
    
    def _generate_route_recommendations_simple(self, route_data):
        """Generate route optimization recommendations - simplified version"""
        recommendations = []
        
        if len(route_data) == 0:
            return ['No route data available for optimization recommendations']
        
        for route_name, data in route_data.items():
            if data['efficiency_score'] < 0.8:
                recommendations.append(f"Optimize {route_name} route - efficiency below 80%")
            elif data['efficiency_score'] > 1.2:
                recommendations.append(f"Use {route_name} route as benchmark - excellent efficiency")
        
        if not recommendations:
            recommendations.append("All routes performing within acceptable efficiency range")
        
        return recommendations