from django import forms
from .models import Trip

class TripForm(forms.ModelForm):
    class Meta:
        model = Trip
        fields = ['truck', 'driver', 'departure_time', 'arrival_time', 'status']
        widgets = {
            'departure_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'arrival_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get("status")
        arrival_time = cleaned_data.get("arrival_time")

        if status == "Completed" and not arrival_time:
            raise forms.ValidationError("Arrival time is required when the trip is Completed.")

        return cleaned_data