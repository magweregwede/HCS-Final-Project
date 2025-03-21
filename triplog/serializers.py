from rest_framework import serializers
from .models import Trip, TripProduct, Product, Driver, Truck, TripRoute

class TripSerializer(serializers.ModelSerializer):
    truck = serializers.PrimaryKeyRelatedField(queryset=Truck.objects.all())  # Ensure Truck is required
    driver = serializers.PrimaryKeyRelatedField(queryset=Driver.objects.all())  # Ensure Driver is required

    class Meta:
        model = Trip
        fields = ['id', 'truck', 'driver', 'departure_time', 'arrival_time', 'status']
        
class TripProductSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = TripProduct
        fields = ['trip', 'product_name', 'quantity', 'unit']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'description']

class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = ['id', 'name', 'license_number', 'contact']

class TruckSerializer(serializers.ModelSerializer):
    truck_company_name = serializers.CharField(source="TruckCompany.name", read_only=True)

    class Meta:
        model = Truck
        fields = ['id', 'plate_number', 'capacity_kg', 'truck_company_name', 'status']