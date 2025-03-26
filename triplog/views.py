from collections import defaultdict
from django.contrib.admin.models import ADDITION, CHANGE, DELETION
from django.shortcuts import render
from django.shortcuts import redirect
from django.urls import reverse
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView
from django.views.generic.edit import UpdateView, DeleteView
from .forms import TripForm, TripProductForm
from .models import TruckCompany, Truck, Route, Driver, Trip, Product, TripProduct, TripRoute
from .utils import log_change
from django.db.models import Q
from datetime import datetime

# Create your views here.

# Truck Company Views
class TruckCompanyListView(ListView):
    model = TruckCompany
    template_name = "truckCompany/truckcompany_list.html"

class TruckCompanyDetailView(DetailView):
    model = TruckCompany
    template_name = "truckCompany/truckcompany_detail.html"


class TruckCompanyUpdateView(UpdateView):
    model = TruckCompany
    fields = (
        "name",
        "contact",
        "email",
        "address",
    )
    template_name = "truckCompany/truckcompany_edit.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        log_change(self.request, self.object, message="updated", action_flag=CHANGE)
        return response


class TruckCompanyDeleteView(DeleteView):
    model = TruckCompany
    template_name = "truckCompany/truckcompany_delete.html"
    success_url = reverse_lazy("truckcompany_list")

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        log_change(self.request, self.object, message="deleted", action_flag=DELETION)
        return super().delete(request, *args, **kwargs)

class TruckCompanyCreateView(CreateView):
    model = TruckCompany
    template_name = "truckCompany/truckcompany_new.html"
    fields = (
        "name",
        "contact",
        "email",
        "address",
    )

    def form_valid(self, form):
        response = super().form_valid(form)
        log_change(self.request, self.object, message="created", action_flag=ADDITION)
        return response

# Truck
class TruckListView(ListView):
    model = Truck
    template_name = "truck/truck_list.html"

class TruckDetailView(DetailView):
    model = Truck
    template_name = "truck/truck_detail.html"


class TruckUpdateView(UpdateView):
    model = Truck
    fields = (
        "plate_number",
        "capacity_kg",
        "truck_company",
        "status",
    )
    template_name = "truck/truck_edit.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        log_change(self.request, self.object, message="updated", action_flag=CHANGE)
        return response



class TruckDeleteView(DeleteView):
    model = Truck
    template_name = "truck/truck_delete.html"
    success_url = reverse_lazy("truck_list")

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        log_change(self.request, self.object, message="deleted", action_flag=DELETION)
        return super().delete(request, *args, **kwargs)

class TruckCreateView(CreateView):
    model = Truck
    template_name = "truck/truck_new.html"
    fields = (
        "plate_number",
        "capacity_kg",
        "truck_company",
        "status",
    )

    def form_valid(self, form):
        response = super().form_valid(form)
        log_change(self.request, self.object, message="created", action_flag=ADDITION)
        return response

# Route
class RouteListView(ListView):
    model = Route
    template_name = "route/route_list.html"

class RouteDetailView(DetailView):
    model = Route
    template_name = "route/route_detail.html"


class RouteUpdateView(UpdateView):
    model = Route
    fields = (
        "origin",
        "destination",
        "distance_km",
        "estimated_time_min",
    )
    template_name = "route/route_edit.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        log_change(self.request, self.object, message="updated", action_flag=CHANGE)
        return response



class RouteDeleteView(DeleteView):
    model = Route
    template_name = "route/route_delete.html"
    success_url = reverse_lazy("route_list")

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        log_change(self.request, self.object, message="deleted", action_flag=DELETION)
        return super().delete(request, *args, **kwargs)

class RouteCreateView(CreateView):
    model = Route
    template_name = "route/route_new.html"
    fields = (
        "origin",
        "destination",
        "distance_km",
        "estimated_time_min",
    )

    def form_valid(self, form):
        response = super().form_valid(form)
        log_change(self.request, self.object, message="created", action_flag=ADDITION)
        return response

# Driver
class DriverListView(ListView):
    model = Driver
    template_name = "driver/driver_list.html"

class DriverDetailView(DetailView):
    model = Driver
    template_name = "driver/driver_detail.html"


class DriverUpdateView(UpdateView):
    model = Driver
    fields = (
        "name",
        "license_number",
        "assigned_truck",
        "contact",
    )
    template_name = "driver/driver_edit.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        log_change(self.request, self.object, message="updated", action_flag=CHANGE)
        return response

class DriverDeleteView(DeleteView):
    model = Driver
    template_name = "driver/driver_delete.html"
    success_url = reverse_lazy("driver_list")

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        log_change(self.request, self.object, message="deleted", action_flag=DELETION)
        return super().delete(request, *args, **kwargs)

class DriverCreateView(CreateView):
    model = Driver
    template_name = "driver/driver_new.html"
    fields = (
        "name",
        "license_number",
        "assigned_truck",
        "contact",
    )

    def form_valid(self, form):
        response = super().form_valid(form)
        log_change(self.request, self.object, message="created", action_flag=ADDITION)
        return response

# Trip
class TripListView(ListView):
    model = Trip
    template_name = "trip/trip_list.html"
    context_object_name = "trip_list"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Search functionality (works independently of date filter)
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(truck__plate_number__icontains=search_query) |
                Q(driver__name__icontains=search_query)
            )
        
        # Date filter (optional)
        departure_date = self.request.GET.get('departure_date')
        if departure_date:
            try:
                date_obj = datetime.strptime(departure_date, '%Y-%m-%d').date()
                queryset = queryset.filter(departure_time__date=date_obj)
            except ValueError:
                pass
        
        # Default sorting
        if self.request.GET.get('sort') == 'departure_time':
            queryset = queryset.order_by('departure_time')
        else:
            queryset = queryset.order_by('-departure_time')  # newest first by default
        
        return queryset.select_related('truck', 'driver')

class TripDetailView(DetailView):
    model = Trip
    template_name = "trip/trip_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tripproducts'] = TripProduct.objects.filter(trip=self.object)
        return context


class TripUpdateView(UpdateView):
    model = Trip
    template_name = "trip/trip_edit.html"
    form_class = TripForm

    def form_valid(self, form):
        response = super().form_valid(form)
        log_change(self.request, self.object, message="updated", action_flag=CHANGE)
        return response



class TripDeleteView(DeleteView):
    model = Trip
    template_name = "trip/trip_delete.html"
    success_url = reverse_lazy("trip_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        log_change(self.request, self.object, message="deleted", action_flag=DELETION)
        return response

class TripCreateView(CreateView):
    model = Trip
    template_name = "trip/trip_new.html"
    form_class = TripForm


    def form_valid(self, form):
        # Automatically set the clerk field to the logged-in user
        form.instance.clerk = self.request.user
        response = super().form_valid(form)
        log_change(self.request, self.object, message="created", action_flag=ADDITION)
        return response
    
    def get_success_url(self):
        return reverse('tripproduct_new', kwargs={'trip_id': self.object.id})  # Redirect to trip product form

# Product
class ProductListView(ListView):
    model = Product
    template_name = "product/product_list.html"

class ProductDetailView(DetailView):
    model = Product
    template_name = "product/product_detail.html"


class ProductUpdateView(UpdateView):
    model = Product
    fields = (
        "name",
        "category",
        "description",
    )
    template_name = "product/product_edit.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        log_change(self.request, self.object, message="updated", action_flag=CHANGE)
        return response


class ProductDeleteView(DeleteView):
    model = Product
    template_name = "product/product_delete.html"
    success_url = reverse_lazy("product_list")

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        log_change(self.request, self.object, message="deleted", action_flag=DELETION)
        return super().delete(request, *args, **kwargs)

class ProductCreateView(CreateView):
    model = Product
    template_name = "product/product_new.html"
    fields = (
        "name",
        "category",
        "description",
    )

    def form_valid(self, form):
        response = super().form_valid(form)
        log_change(self.request, self.object, message="created", action_flag=ADDITION)
        return response

# Trip Product
class TripProductListView(ListView):
    model = TripProduct
    template_name = "tripProduct/tripproduct_list.html"
    context_object_name = "grouped_tripproducts"

    def get_queryset(self):
        """ Group trip products by trip. """
        grouped_products = defaultdict(list)
        for tripproduct in TripProduct.objects.select_related("trip", "trip__truck", "trip__driver", "product"):
            grouped_products[tripproduct.trip].append(tripproduct)

        return dict(grouped_products)  # Convert defaultdict to a regular dict for template use

class TripProductDetailView(DetailView):
    model = TripProduct
    template_name = "tripProduct/tripproduct_detail.html"


class TripProductUpdateView(UpdateView):
    model = TripProduct
    fields = (
        "trip",
        "product",
        "quantity",
        "unit",
    )
    template_name = "tripProduct/tripproduct_edit.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        log_change(self.request, self.object, message="updated", action_flag=CHANGE)
        return response


class TripProductDeleteView(DeleteView):
    model = TripProduct
    template_name = "tripProduct/tripproduct_delete.html"
    success_url = reverse_lazy("tripproduct_list")

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        log_change(self.request, self.object, message="deleted", action_flag=DELETION)
        return super().delete(request, *args, **kwargs)

class TripProductCreateView(CreateView):
    model = TripProduct
    form_class = TripProductForm
    template_name = "tripProduct/tripproduct_new.html"


    def form_valid(self, form):
        trip = Trip.objects.get(id=self.kwargs['trip_id'])  # Get the trip ID from URL
        trip_product = form.save(commit=False)
        trip_product.trip = trip  # Assign the trip
        trip_product.save()
        response = super().form_valid(form)
        log_change(self.request, self.object, message="created", action_flag=ADDITION)

        # Check which button was clicked
        if "save_and_add_another" in self.request.POST:
            return redirect(reverse("tripproduct_new", kwargs={"trip_id": trip.id}))  # Stay on form
        else:
            return redirect(reverse("triproute_new", kwargs={"trip_id": trip.id}))  # Move to next step
        # return response

# Trip Route
class TripRouteListView(ListView):
    model = TripRoute
    template_name = "tripRoute/triproute_list.html"

class TripRouteDetailView(DetailView):
    model = TripRoute
    template_name = "tripRoute/triproute_detail.html"

class TripRouteUpdateView(UpdateView):
    model = TripRoute
    fields = (
        "trip",
        "route",
        "actual_time_min",
    )
    template_name = "tripRoute/triproute_edit.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        log_change(self.request, self.object, message="updated", action_flag=CHANGE)
        return response



class TripRouteDeleteView(DeleteView):
    model = TripRoute
    template_name = "tripRoute/triproute_delete.html"
    success_url = reverse_lazy("triproute_list")

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        log_change(self.request, self.object, message="deleted", action_flag=DELETION)
        return super().delete(request, *args, **kwargs)

class TripRouteCreateView(CreateView):
    model = TripRoute
    template_name = "tripRoute/triproute_new.html"
    fields = ['route']  # Exclude 'trip' since we auto-assign it

    def form_valid(self, form):
        trip_id = self.kwargs.get('trip_id')  # Get trip_id from the URL
        form.instance.trip_id = trip_id  # Assign trip automatically
        response = super().form_valid(form)
        log_change(self.request, self.object, message="created", action_flag=ADDITION)
        return response
    
    def get_success_url(self):
        return reverse('trip_detail', kwargs={'pk': self.object.trip.id})  # Redirect to trip details page