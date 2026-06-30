from django import forms


class GridCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    template_name = "vehicles/widgets/grid_checkbox_select.html"


class DatalistTextInput(forms.TextInput):
    """Text input with HTML datalist suggestions; any value remains valid."""

    template_name = "vehicles/widgets/datalist_text.html"

    def __init__(self, *, datalist_id: str, options: tuple[str, ...], **kwargs):
        super().__init__(**kwargs)
        self.datalist_id = datalist_id
        self.options = options

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["widget"]["datalist_id"] = self.datalist_id
        context["widget"]["options"] = self.options
        context["widget"]["attrs"]["list"] = self.datalist_id
        return context
