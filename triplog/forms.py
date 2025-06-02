from django import forms
from .models import Trip, TripProduct, Driver
from drivers.models import DriverAvailability

class TripForm(forms.ModelForm):
    class Meta:
        model = Trip
        fields = ['driver', 'departure_time', 'arrival_time', 'status']
        widgets = {
            'departure_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'arrival_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter drivers to show only available ones
        available_driver_ids = DriverAvailability.objects.filter(
            is_available=True
        ).values_list('triplog_driver_id', flat=True)
        
        self.fields['driver'].queryset = Driver.objects.filter(
            id__in=available_driver_ids
        )
        
        # Update the field label to indicate availability filtering
        self.fields['driver'].label = "Available Drivers"
        self.fields['driver'].help_text = "Only showing currently available drivers"

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get("status")
        arrival_time = cleaned_data.get("arrival_time")

        if status == "Completed" and not arrival_time:
            raise forms.ValidationError("Arrival time is required when the trip is Completed.")

        return cleaned_data
    
class TripProductForm(forms.ModelForm):
    class Meta:
        model = TripProduct
        fields = ['product', 'quantity', 'unit']