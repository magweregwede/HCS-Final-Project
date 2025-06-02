from django.urls import path
from . import views

app_name = 'drivers'

urlpatterns = [
    path('', views.driver_availability_dashboard, name='availability_dashboard'),
    path('update/', views.update_driver_availability, name='update_availability'),
    path('toggle/', views.toggle_driver_availability, name='toggle_availability'),
    path('available-drivers/', views.get_available_drivers_api, name='available_drivers_api'),
]