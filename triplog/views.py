from collections import defaultdict
from django.contrib.admin.models import ADDITION, CHANGE, DELETION
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.management import call_command
from django.shortcuts import render
from django.shortcuts import redirect
from django.urls import reverse
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView
from django.views.generic.edit import UpdateView, DeleteView
from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import TripForm, TripProductForm
from .models import TruckCompany, Truck, Route, Driver, Trip, Product, TripProduct, TripRoute
from .utils.utils import log_change
from .utils.permissions import (
    ManagerRequiredMixin, ClerkOrManagerRequiredMixin, LogisticsReadOnlyMixin,
    LogisticsEditMixin, DriverClerkManagerMixin, is_clerk, is_manager, is_driver,
    is_clerk_or_manager, is_driver_clerk_or_manager
)
from django.db.models import Q
from datetime import datetime
from triplog.stats import get_trip_stats
from .models import DriverLeaderboard, MonthlyDriverRanking

import os
import glob
import json
from django.http import FileResponse, Http404, JsonResponse
from django.conf import settings
from django.apps import apps


# Create your views here.

# Dashboard View - Clerks and Managers only
class DashboardView(ClerkOrManagerRequiredMixin, TemplateView):
    template_name = "dashboard.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetching stats from the utility function
        context['stats'] = get_trip_stats()
        # Add user permissions to context
        context['is_manager'] = is_manager(self.request.user)
        context['is_clerk'] = is_clerk(self.request.user)
        context['is_driver'] = is_driver(self.request.user)
        return context
    
    def post(self, request, *args, **kwargs):
        stats = get_trip_stats()
        return JsonResponse(stats, safe=False)

class ReportingView(LoginRequiredMixin, TemplateView):
    template_name = "reporting/reporting.html"
    login_url = '/accounts/login/'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add user permissions to context for template rendering
        context['is_manager'] = is_manager(self.request.user)
        context['is_clerk'] = is_clerk(self.request.user)
        context['is_driver'] = is_driver(self.request.user)
        return context

# Truck Company Views (Logistics Partners - Read only for clerks, edit for managers)
class TruckCompanyListView(LogisticsReadOnlyMixin, ListView):
    model = TruckCompany
    template_name = "truckCompany/truckcompany_list.html"

class TruckCompanyDetailView(LogisticsReadOnlyMixin, DetailView):
    model = TruckCompany
    template_name = "truckCompany/truckcompany_detail.html"

class TruckCompanyUpdateView(LogisticsEditMixin, UpdateView):
    model = TruckCompany
    fields = ("name", "contact", "email", "address")
    template_name = "truckCompany/truckcompany_edit.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        log_change(self.request, self.object, message="updated", action_flag=CHANGE)
        return response

class TruckCompanyDeleteView(LogisticsEditMixin, DeleteView):
    model = TruckCompany
    template_name = "truckCompany/truckcompany_delete.html"
    success_url = reverse_lazy("truckcompany_list")

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        log_change(self.request, self.object, message="deleted", action_flag=DELETION)
        return super().delete(request, *args, **kwargs)

class TruckCompanyCreateView(LogisticsEditMixin, CreateView):
    model = TruckCompany
    template_name = "truckCompany/truckcompany_new.html"
    fields = ("name", "contact", "email", "address")

    def form_valid(self, form):
        response = super().form_valid(form)
        log_change(self.request, self.object, message="created", action_flag=ADDITION)
        return response

# Truck Views (Logistics Partners - Read only for clerks, edit for managers)
class TruckListView(LogisticsReadOnlyMixin, ListView):
    model = Truck
    template_name = "truck/truck_list.html"

class TruckDetailView(LogisticsReadOnlyMixin, DetailView):
    model = Truck
    template_name = "truck/truck_detail.html"

class TruckUpdateView(LogisticsEditMixin, UpdateView):
    model = Truck
    fields = ("plate_number", "capacity_kg", "truck_company", "status")
    template_name = "truck/truck_edit.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        log_change(self.request, self.object, message="updated", action_flag=CHANGE)
        return response

class TruckDeleteView(LogisticsEditMixin, DeleteView):
    model = Truck
    template_name = "truck/truck_delete.html"
    success_url = reverse_lazy("truck_list")

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        log_change(self.request, self.object, message="deleted", action_flag=DELETION)
        return super().delete(request, *args, **kwargs)

class TruckCreateView(LogisticsEditMixin, CreateView):
    model = Truck
    template_name = "truck/truck_new.html"
    fields = ("plate_number", "capacity_kg", "truck_company", "status")

    def form_valid(self, form):
        response = super().form_valid(form)
        log_change(self.request, self.object, message="created", action_flag=ADDITION)
        return response

# Route Views (Logistics Partners - Read only for clerks, edit for managers)
class RouteListView(LogisticsReadOnlyMixin, ListView):
    model = Route
    template_name = "route/route_list.html"

class RouteDetailView(LogisticsReadOnlyMixin, DetailView):
    model = Route
    template_name = "route/route_detail.html"

class RouteUpdateView(LogisticsEditMixin, UpdateView):
    model = Route
    fields = ("origin", "destination", "distance_km", "estimated_time_min")
    template_name = "route/route_edit.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        log_change(self.request, self.object, message="updated", action_flag=CHANGE)
        return response

class RouteDeleteView(LogisticsEditMixin, DeleteView):
    model = Route
    template_name = "route/route_delete.html"
    success_url = reverse_lazy("route_list")

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        log_change(self.request, self.object, message="deleted", action_flag=DELETION)
        return super().delete(request, *args, **kwargs)

class RouteCreateView(LogisticsEditMixin, CreateView):
    model = Route
    template_name = "route/route_new.html"
    fields = ("origin", "destination", "distance_km", "estimated_time_min")

    def form_valid(self, form):
        response = super().form_valid(form)
        log_change(self.request, self.object, message="created", action_flag=ADDITION)
        return response

# Driver Views (Deliveries - Clerks and Managers can access)
class DriverListView(ClerkOrManagerRequiredMixin, ListView):
    model = Driver
    template_name = "driver/driver_list.html"
    context_object_name = "driver_list"

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(assigned_truck__plate_number__icontains=search_query) |
                Q(assigned_truck__truck_company__name__icontains=search_query)
            )
        return queryset.select_related('assigned_truck__truck_company')

class DriverDetailView(ClerkOrManagerRequiredMixin, DetailView):
    model = Driver
    template_name = "driver/driver_detail.html"

class DriverUpdateView(ClerkOrManagerRequiredMixin, UpdateView):
    model = Driver
    fields = ("name", "license_number", "assigned_truck", "contact")
    template_name = "driver/driver_edit.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        log_change(self.request, self.object, message="updated", action_flag=CHANGE)
        return response

class DriverDeleteView(ManagerRequiredMixin, DeleteView):
    model = Driver
    template_name = "driver/driver_delete.html"
    success_url = reverse_lazy("driver_list")

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        log_change(self.request, self.object, message="deleted", action_flag=DELETION)
        return super().delete(request, *args, **kwargs)

class DriverCreateView(ManagerRequiredMixin, CreateView):
    model = Driver
    template_name = "driver/driver_new.html"
    fields = ("name", "license_number", "assigned_truck", "contact")

    def form_valid(self, form):
        response = super().form_valid(form)
        log_change(self.request, self.object, message="created", action_flag=ADDITION)
        return response

# Trip Views (Deliveries - Clerks and Managers can access)
class TripListView(ClerkOrManagerRequiredMixin, ListView):
    model = Trip
    template_name = "trip/trip_list.html"
    context_object_name = "trip_list"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(status="Ongoing")
        
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(truck__plate_number__icontains=search_query) |
                Q(driver__name__icontains=search_query)
            )
        
        departure_date = self.request.GET.get('departure_date')
        if departure_date:
            try:
                date_obj = datetime.strptime(departure_date, '%Y-%m-%d').date()
                queryset = queryset.filter(departure_time__date=date_obj)
            except ValueError:
                pass

        if self.request.GET.get('sort') == 'departure_time':
            queryset = queryset.order_by('departure_time')
        else:
            queryset = queryset.order_by('-departure_time')
        
        return queryset.select_related('truck', 'driver')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status'] = "ongoing"
        return context

class TripDetailView(ClerkOrManagerRequiredMixin, DetailView):
    model = Trip
    template_name = "trip/trip_detail.html"
    context_object_name = "trip"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['trip_routes'] = TripRoute.objects.filter(trip=self.object)
        context['tripproducts'] = TripProduct.objects.filter(trip=self.object)
        return context

class TripUpdateView(ClerkOrManagerRequiredMixin, UpdateView):
    model = Trip
    template_name = "trip/trip_edit.html"
    form_class = TripForm

    def form_valid(self, form):
        response = super().form_valid(form)
        log_change(self.request, self.object, message="updated", action_flag=CHANGE)
        return response

class TripDeleteView(ClerkOrManagerRequiredMixin, DeleteView):
    model = Trip
    template_name = "trip/trip_delete.html"
    success_url = reverse_lazy("trip_list")

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            trip_route = self.object.triproute
            trip_route.delete()
        except TripRoute.DoesNotExist:
            pass
        return super().delete(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        log_change(self.request, self.object, message="deleted", action_flag=DELETION)
        return response

class TripCreateView(ClerkOrManagerRequiredMixin, CreateView):
    model = Trip
    template_name = "trip/trip_new.html"
    form_class = TripForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == 'GET':
            driver_id = self.request.GET.get('driver')
            if driver_id:
                try:
                    context['selected_driver'] = int(driver_id)
                    driver = Driver.objects.get(pk=driver_id)
                    context['assigned_truck'] = driver.assigned_truck
                except (ValueError, Driver.DoesNotExist):
                    pass
        return context

    def form_valid(self, form):
        form.instance.clerk = self.request.user
        driver = form.cleaned_data.get('driver')
        if driver and hasattr(driver, 'assigned_truck'):
            form.instance.truck = driver.assigned_truck
            form.instance.clerk = self.request.user
        else:
            form.add_error('driver', "Selected driver has no assigned truck")
            return self.form_invalid(form)
        response = super().form_valid(form)
        log_change(self.request, self.object, message="created", action_flag=ADDITION)
        return response
    
    def get_success_url(self):
        return reverse('tripproduct_new', kwargs={'trip_id': self.object.id})

# Product Views (Deliveries - Clerks and Managers can access)
class ProductListView(ClerkOrManagerRequiredMixin, ListView):
    model = Product
    template_name = "product/product_list.html"

class ProductDetailView(ClerkOrManagerRequiredMixin, DetailView):
    model = Product
    template_name = "product/product_detail.html"

class ProductUpdateView(ManagerRequiredMixin, UpdateView):
    model = Product
    fields = ("name", "category", "description")
    template_name = "product/product_edit.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        log_change(self.request, self.object, message="updated", action_flag=CHANGE)
        return response

class ProductDeleteView(ManagerRequiredMixin, DeleteView):
    model = Product
    template_name = "product/product_delete.html"
    success_url = reverse_lazy("product_list")

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        log_change(self.request, self.object, message="deleted", action_flag=DELETION)
        return super().delete(request, *args, **kwargs)

class ProductCreateView(ManagerRequiredMixin, CreateView):
    model = Product
    template_name = "product/product_new.html"
    fields = ("name", "category", "description")

    def form_valid(self, form):
        response = super().form_valid(form)
        log_change(self.request, self.object, message="created", action_flag=ADDITION)
        return response

# Trip Product Views (Deliveries - Clerks and Managers can access)
class TripProductListView(ClerkOrManagerRequiredMixin, ListView):
    model = TripProduct
    template_name = "tripProduct/tripproduct_list.html"
    context_object_name = "grouped_tripproducts"

    def get_queryset(self):
        grouped_products = defaultdict(list)
        for tripproduct in TripProduct.objects.select_related("trip", "trip__truck", "trip__driver", "product"):
            grouped_products[tripproduct.trip].append(tripproduct)
        return dict(grouped_products)

class TripProductDetailView(ClerkOrManagerRequiredMixin, DetailView):
    model = TripProduct
    template_name = "tripProduct/tripproduct_detail.html"

class TripProductUpdateView(ClerkOrManagerRequiredMixin, UpdateView):
    model = TripProduct
    fields = ("trip", "product", "quantity", "unit")
    template_name = "tripProduct/tripproduct_edit.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        log_change(self.request, self.object, message="updated", action_flag=CHANGE)
        return response

class TripProductDeleteView(ClerkOrManagerRequiredMixin, DeleteView):
    model = TripProduct
    template_name = "tripProduct/tripproduct_delete.html"
    success_url = reverse_lazy("tripproduct_list")

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        log_change(self.request, self.object, message="deleted", action_flag=DELETION)
        return super().delete(request, *args, **kwargs)

class TripProductCreateView(ClerkOrManagerRequiredMixin, CreateView):
    model = TripProduct
    form_class = TripProductForm
    template_name = "tripProduct/tripproduct_new.html"

    def form_valid(self, form):
        trip = Trip.objects.get(id=self.kwargs['trip_id'])
        trip_product = form.save(commit=False)
        trip_product.trip = trip
        trip_product.save()
        response = super().form_valid(form)
        log_change(self.request, self.object, message="created", action_flag=ADDITION)

        if "save_and_add_another" in self.request.POST:
            return redirect(reverse("tripproduct_new", kwargs={"trip_id": trip.id}))
        else:
            return redirect(reverse("triproute_new", kwargs={"trip_id": trip.id}))

# Trip Route Views (Deliveries - Clerks and Managers can access)
class TripRouteListView(ClerkOrManagerRequiredMixin, ListView):
    model = TripRoute
    template_name = "tripRoute/triproute_list.html"
    paginate_by = 10
    context_object_name = 'triproute_list'

    def get_queryset(self):
        queryset = super().get_queryset().select_related('trip', 'route')
        search = self.request.GET.get('search')
        origin = self.request.GET.get('origin')
        destination = self.request.GET.get('destination')

        if search:
            queryset = queryset.filter(
                Q(trip__truck__plate_number__icontains=search) |
                Q(trip__driver__name__icontains=search) |
                Q(route__origin__icontains=search) |
                Q(route__destination__icontains=search)
            )
        
        if origin:
            queryset = queryset.filter(route__origin__icontains=origin)
        
        if destination:
            queryset = queryset.filter(route__destination__icontains=destination)

        return queryset

class TripRouteDetailView(ClerkOrManagerRequiredMixin, DetailView):
    model = TripRoute
    template_name = "tripRoute/triproute_detail.html"

class TripRouteUpdateView(ClerkOrManagerRequiredMixin, UpdateView):
    model = TripRoute
    fields = ("trip", "route", "actual_time_min")
    template_name = "tripRoute/triproute_edit.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        log_change(self.request, self.object, message="updated", action_flag=CHANGE)
        return response

class TripRouteDeleteView(ClerkOrManagerRequiredMixin, DeleteView):
    model = TripRoute
    template_name = "tripRoute/triproute_delete.html"
    success_url = reverse_lazy("triproute_list")

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        log_change(self.request, self.object, message="deleted", action_flag=DELETION)
        return super().delete(request, *args, **kwargs)

class TripRouteCreateView(ClerkOrManagerRequiredMixin, CreateView):
    model = TripRoute
    template_name = "tripRoute/triproute_new.html"
    fields = ['route']

    def form_valid(self, form):
        trip_id = self.kwargs.get('trip_id')
        form.instance.trip_id = trip_id
        response = super().form_valid(form)
        log_change(self.request, self.object, message="created", action_flag=ADDITION)
        return response
    
    def get_success_url(self):
        return reverse('trip_detail', kwargs={'pk': self.object.trip.id})

# Reporting Views
@login_required
@user_passes_test(is_driver_clerk_or_manager, login_url='/accounts/login/')
def driver_leaderboard(request):
    """Display the overall driver leaderboard - accessible to drivers, clerks, and managers"""
    leaderboard = DriverLeaderboard.objects.all()[:10]
    recent_rankings = MonthlyDriverRanking.objects.select_related().order_by('-month', 'rank')[:15]
    
    context = {
        'leaderboard': leaderboard,
        'recent_rankings': recent_rankings,
        'is_manager': is_manager(request.user),
        'is_clerk': is_clerk(request.user),
        'is_driver': is_driver(request.user),
    }
    return render(request, 'reporting/leaderboard.html', context)

@login_required
@user_passes_test(is_manager, login_url='/accounts/login/')
def latest_report_download(request):
    """Download the latest report - managers only"""
    
    reports_dir = os.path.join(settings.BASE_DIR, 'reports')
    
    if not os.path.exists(reports_dir):
        return JsonResponse({'error': 'Reports directory not found'}, status=404)
    
    pdf_files = glob.glob(os.path.join(reports_dir, '*.pdf'))
    
    if not pdf_files:
        return JsonResponse({'error': 'No reports available'}, status=404)
    
    latest_file = max(pdf_files, key=os.path.getmtime)
    
    try:
        response = FileResponse(
            open(latest_file, 'rb'),
            content_type='application/pdf',
            as_attachment=True,
            filename=os.path.basename(latest_file)
        )
        return response
    except Exception as e:
        return JsonResponse({'error': f'Error serving file: {str(e)}'}, status=500)

@login_required
@user_passes_test(is_manager, login_url='/accounts/login/')
def reports_info(request):
    """Get information about available reports - managers only"""
    
    triplog_config = apps.get_app_config('triplog')
    app_path = triplog_config.path
    reports_dir = os.path.join(app_path, 'reports')
    
    if not os.path.exists(reports_dir):
        return JsonResponse({'error': 'Reports directory not found'}, status=404)
    
    pdf_files = glob.glob(os.path.join(reports_dir, '*.pdf'))
    
    if not pdf_files:
        return JsonResponse({'reports': [], 'latest': None})
    
    reports_info = []
    for file_path in pdf_files:
        file_stat = os.stat(file_path)
        reports_info.append({
            'filename': os.path.basename(file_path),
            'size': file_stat.st_size,
            'modified': file_stat.st_mtime,
            'path': file_path
        })
    
    reports_info.sort(key=lambda x: x['modified'], reverse=True)
    latest_report = reports_info[0] if reports_info else None
    
    return JsonResponse({
        'reports': reports_info,
        'latest': latest_report,
        'total_count': len(reports_info)
    })

@login_required
@user_passes_test(is_manager, login_url='/accounts/login/')
def predictive_analytics_dashboard(request):
    """Predictive analytics dashboard view - managers only"""
    
    try:
        call_command('generate_predictive_analysis')
    except Exception as e:
        print(f"Error generating analysis: {e}")
    
    results_path = os.path.join('reports', 'predictive_analysis.json')
    analysis_data = {}
    
    if os.path.exists(results_path):
        with open(results_path, 'r') as f:
            analysis_data = json.load(f)
    
    context = {
        'analysis_data': analysis_data,
        'page_title': 'Predictive Analytics Dashboard'
    }
    
    return render(request, 'reporting/predictive_analytics.html', context)

@login_required
@user_passes_test(is_manager, login_url='/accounts/login/')
def predictive_analysis_api(request):
    """API endpoint for predictive analysis data - managers only"""
    
    results_path = os.path.join('reports', 'predictive_analysis.json')
    
    if os.path.exists(results_path):
        with open(results_path, 'r') as f:
            data = json.load(f)
        return JsonResponse(data)
    
    return JsonResponse({'error': 'Analysis data not available'}, status=404)

