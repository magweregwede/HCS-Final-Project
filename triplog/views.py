from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView
from django.views.generic.edit import UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import TruckCompany

# Create your views here.

# Truck Company Views
class TruckCompanyListView(ListView):
    model = TruckCompany
    template_name = "truckCompany/truckcompany_list.html"

class TruckCompanyDetailView(DetailView):  # new
    model = TruckCompany
    template_name = "truckCompany/truckcompany_detail.html"


class TruckCompanyUpdateView(UpdateView):  # new
    model = TruckCompany
    fields = (
        "name",
        "contact",
        "email",
        "address",
    )
    template_name = "truckCompany/truckcompany_edit.html"


class TruckCompanyDeleteView(DeleteView):  # new
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