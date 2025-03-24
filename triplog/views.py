from django.shortcuts import render
from django.shortcuts import redirect
from django.views.generic import ListView, DetailView, CreateView
from django.views.generic.edit import UpdateView, DeleteView
from django.urls import reverse_lazy
from .forms import TripForm
from .models import TruckCompany, Truck, Route, Driver, Trip

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


class TruckCompanyDeleteView(DeleteView):
    model = TruckCompany
    template_name = "truckCompany/truckcompany_delete.html"
    success_url = reverse_lazy("truckcompany_list")

class TruckCompanyCreateView(CreateView):
    model = TruckCompany
    template_name = "truckCompany/truckcompany_new.html"
    fields = (
        "name",
        "contact",
        "email",
        "address",
    )

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


class TruckDeleteView(DeleteView):
    model = Truck
    template_name = "truck/truck_delete.html"
    success_url = reverse_lazy("truck_list")

class TruckCreateView(CreateView):
    model = Truck
    template_name = "truck/truck_new.html"
    fields = (
        "plate_number",
        "capacity_kg",
        "truck_company",
        "status",
    )

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


class RouteDeleteView(DeleteView):
    model = Route
    template_name = "route/route_delete.html"
    success_url = reverse_lazy("route_list")

class RouteCreateView(CreateView):
    model = Route
    template_name = "route/route_new.html"
    fields = (
        "origin",
        "destination",
        "distance_km",
        "estimated_time_min",
    )

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


class DriverDeleteView(DeleteView):
    model = Driver
    template_name = "driver/driver_delete.html"
    success_url = reverse_lazy("driver_list")

class DriverCreateView(CreateView):
    model = Driver
    template_name = "driver/driver_new.html"
    fields = (
        "name",
        "license_number",
        "assigned_truck",
        "contact",
    )

# Trip
class TripListView(ListView):
    model = Trip
    template_name = "trip/trip_list.html"

class TripDetailView(DetailView):
    model = Trip
    template_name = "trip/trip_detail.html"


class TripUpdateView(UpdateView):
    model = Trip
    template_name = "trip/trip_edit.html"
    form_class = TripForm


class TripDeleteView(DeleteView):
    model = Trip
    template_name = "trip/trip_delete.html"
    success_url = reverse_lazy("trip_list")

class TripCreateView(CreateView):
    model = Trip
    template_name = "trip/trip_new.html"
    form_class = TripForm

    def form_valid(self, form):
        # Automatically set the clerk field to the logged-in user
        form.instance.clerk = self.request.user
        return super().form_valid(form)

