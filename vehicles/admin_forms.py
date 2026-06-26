from django import forms

from vehicles.make_options import POPULAR_VEHICLE_MAKES
from vehicles.models import Vehicle
from vehicles.widgets import DatalistTextInput


class VehicleAdminForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = "__all__"
        widgets = {
            "make": DatalistTextInput(
                datalist_id="vehicle-make-options",
                options=POPULAR_VEHICLE_MAKES,
            ),
        }
