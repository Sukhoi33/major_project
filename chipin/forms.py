from django import forms
from .models import Aircraft


class AircraftForm(forms.ModelForm):
    class Meta:
        model = Aircraft
        fields = [
            'registration', 'model',
            'fuel_consumption', 'fuel_unit',
            'speed_unit',
            'vso', 'vs1', 'vr', 'vx', 'vy',
            'vfe', 'vno', 'vne', 'va', 'vlo', 'vle',
        ]

    def clean_fuel_consumption(self):
        value = self.cleaned_data.get('fuel_consumption')
        if value is not None and value <= 0:
            raise forms.ValidationError("Fuel consumption must be a positive number.")
        return value

    def clean(self):
        cleaned = super().clean()
        # Ensure any supplied V-speed is positive
        vspeed_fields = ['vso', 'vs1', 'vr', 'vx', 'vy', 'vfe', 'vno', 'vne', 'va', 'vlo', 'vle']
        for field in vspeed_fields:
            val = cleaned.get(field)
            if val is not None and val <= 0:
                self.add_error(field, "Speed must be a positive number.")
        return cleaned
