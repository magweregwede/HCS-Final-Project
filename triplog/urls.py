from django.urls import path

from .views import (
    TruckCompanyListView,
    TruckCompanyDetailView,
    TruckCompanyUpdateView,
    TruckCompanyDeleteView,
)

urlpatterns = [
    path("truckcompany/", TruckCompanyListView.as_view(), name="truckcompany_list"),
    path("truckcompany/<int:pk>/", TruckCompanyDetailView.as_view(), name="truckcompany_detail"),
    path("truckcompany/<int:pk>/edit", TruckCompanyUpdateView.as_view(), name="truckcompany_edit"),
    path("truckcompany/<int:pk>/delete", TruckCompanyDeleteView.as_view(), name="truckcompany_delete"),
]