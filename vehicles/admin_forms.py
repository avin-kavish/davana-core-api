from django import forms

from vehicles.make_options import POPULAR_VEHICLE_MAKES
from vehicles.models import Vehicle, VehiclePhoto
from vehicles.widgets import DatalistTextInput, GridCheckboxSelectMultiple


class VehicleAdminForm(forms.ModelForm):
    features = forms.MultipleChoiceField(
        choices=Vehicle.FEATURE_CHOICES,
        widget=GridCheckboxSelectMultiple,
        required=False,
    )

    class Media:
        css = {"all": ("vehicles/admin_vehicle_form.css",)}

    class Meta:
        model = Vehicle
        fields = "__all__"
        widgets = {
            "make": DatalistTextInput(
                datalist_id="vehicle-make-options",
                options=POPULAR_VEHICLE_MAKES,
            ),
        }


class VehiclePhotoInlineForm(forms.ModelForm):
    class Meta:
        model = VehiclePhoto
        fields = "__all__"
        widgets = {
            "description": forms.Textarea(
                attrs={
                    "rows": 3,
                    "style": "box-sizing: border-box;",
                }
            ),
        }
