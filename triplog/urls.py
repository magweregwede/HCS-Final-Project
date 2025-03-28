from django.urls import path

from .views import (
    # Truck Company
    TruckCompanyListView,
    TruckCompanyDetailView,
    TruckCompanyUpdateView,
    TruckCompanyDeleteView,
    TruckCompanyCreateView,
    # Truck
    TruckListView,
    TruckDetailView,
    TruckUpdateView,
    TruckDeleteView,
    TruckCreateView,
    # Route
    RouteListView,
    RouteDetailView,
    RouteUpdateView,
    RouteDeleteView,
    RouteCreateView,
    # Driver
    DriverListView,
    DriverDetailView,
    DriverUpdateView,
    DriverDeleteView,
    DriverCreateView,
    # Trip
    TripListView,
    TripDetailView,
    TripUpdateView,
    TripDeleteView,
    TripCreateView,
    # Product
    ProductListView,
    ProductDetailView,
    ProductUpdateView,
    ProductDeleteView,
    ProductCreateView,
    # Trip Product
    TripProductListView,
    TripProductDetailView,
    TripProductUpdateView,
    TripProductDeleteView,
    TripProductCreateView,
    # Trip Route
    TripRouteListView,
    TripRouteDetailView,
    TripRouteUpdateView,
    TripRouteDeleteView,
    TripRouteCreateView,
)

urlpatterns = [
    # truck company
    path("truckcompany/", TruckCompanyListView.as_view(), name="truckcompany_list"),
    path("truckcompany/<int:pk>/", TruckCompanyDetailView.as_view(), name="truckcompany_detail"),
    path("truckcompany/<int:pk>/edit", TruckCompanyUpdateView.as_view(), name="truckcompany_edit"),
    path("truckcompany/<int:pk>/delete", TruckCompanyDeleteView.as_view(), name="truckcompany_delete"),
    path("truckcompany/new/", TruckCompanyCreateView.as_view(), name="truckcompany_new"),
    # truck
    path("truck/", TruckListView.as_view(), name="truck_list"),
    path("truck/<int:pk>/", TruckDetailView.as_view(), name="truck_detail"),
    path("truck/<int:pk>/edit", TruckUpdateView.as_view(), name="truck_edit"),
    path("truck/<int:pk>/delete", TruckDeleteView.as_view(), name="truck_delete"),
    path("truck/new/", TruckCreateView.as_view(), name="truck_new"),
    # route
    path("route/", RouteListView.as_view(), name="route_list"),
    path("route/<int:pk>/", RouteDetailView.as_view(), name="route_detail"),
    path("route/<int:pk>/edit", RouteUpdateView.as_view(), name="route_edit"),
    path("route/<int:pk>/delete", RouteDeleteView.as_view(), name="route_delete"),
    path("route/new/", RouteCreateView.as_view(), name="route_new"),
    # Driver
    path("driver/", DriverListView.as_view(), name="driver_list"),
    path("driver/<int:pk>/", DriverDetailView.as_view(), name="driver_detail"),
    path("driver/<int:pk>/edit", DriverUpdateView.as_view(), name="driver_edit"),
    path("driver/<int:pk>/delete", DriverDeleteView.as_view(), name="driver_delete"),
    path("driver/new/", DriverCreateView.as_view(), name="driver_new"),
    # Trip
    path("trip/", TripListView.as_view(), name="trip_list"),
    path("trip/<int:pk>/", TripDetailView.as_view(), name="trip_detail"),
    path("trip/<int:pk>/edit", TripUpdateView.as_view(), name="trip_edit"),
    path("trip/<int:pk>/delete", TripDeleteView.as_view(), name="trip_delete"),
    path("trip/new/", TripCreateView.as_view(), name="trip_new"),
    # Product
    path("product/", ProductListView.as_view(), name="product_list"),
    path("product/<int:pk>/", ProductDetailView.as_view(), name="product_detail"),
    #  ### Following urls disabled for Product data safety
    path("product/<int:pk>/edit", ProductUpdateView.as_view(), name="product_edit"),
    path("product/<int:pk>/delete", ProductDeleteView.as_view(), name="product_delete"),
    path("product/new/", ProductCreateView.as_view(), name="product_new"),
    path('trip/<int:trip_id>/product/new/', TripProductCreateView.as_view(), name='tripproduct_new'),  # Accepts trip_id
    # Trip Product
    path("tripproduct/", TripProductListView.as_view(), name="tripproduct_list"),
    path("tripproduct/<int:pk>/", TripProductDetailView.as_view(), name="tripproduct_detail"),
    path("tripproduct/<int:pk>/edit", TripProductUpdateView.as_view(), name="tripproduct_edit"),
    path("tripproduct/<int:pk>/delete", TripProductDeleteView.as_view(), name="tripproduct_delete"),
    path("tripproduct/new/", TripProductCreateView.as_view(), name="tripproduct_new"),
    #  Trip Route
    path("triproute/", TripRouteListView.as_view(), name="triproute_list"),
    path("triproute/<int:pk>/", TripRouteDetailView.as_view(), name="triproute_detail"),
    path("triproute/<int:pk>/edit", TripRouteUpdateView.as_view(), name="triproute_edit"),
    path("triproute/<int:pk>/delete", TripRouteDeleteView.as_view(), name="triproute_delete"),
    path("triproute/new/", TripRouteCreateView.as_view(), name="triproute_new"),
    path('trip/<int:trip_id>/route/new/', TripRouteCreateView.as_view(), name='triproute_new'),  # Accepts trip_id
]