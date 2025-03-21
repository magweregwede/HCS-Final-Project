from django.contrib import admin
from .models import Driver, Product, Route, Trip, TripProduct, TripRoute, Truck, TruckCompany

# Register your models here.
admin.site.register(Driver)
admin.site.register(Product)
admin.site.register(Route)
admin.site.register(Truck)
admin.site.register(TruckCompany)
admin.site.register(Trip)
admin.site.register(TripProduct)
admin.site.register(TripRoute)
