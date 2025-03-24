from import_export import resources
from .models import Trip

class TripResource(resources.ModelResource):
    class Meta:
        model = Trip