from django import forms
from .models import Aircraft, AircraftDocument

ALLOWED_EXTENSIONS = ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.webp']

class AircraftForm(forms.ModelForm):
    class Meta:
        model = Aircraft
        fields = [
            'registration', 'model',
            'fuel_consumption', 'max_fuel',
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
        vspeed_fields = ['vso', 'vs1', 'vr', 'vx', 'vy', 'vfe', 'vno', 'vne', 'va', 'vlo', 'vle']
        for field in vspeed_fields:
            val = cleaned.get(field)
            if val is not None and val <= 0:
                self.add_error(field, "Speed must be a positive number.")
        return cleaned


class AircraftDocumentForm(forms.ModelForm):
    class Meta:
        model = AircraftDocument
        fields = ['name', 'file']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g. Pre-start checklist'}),
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            import os
            ext = os.path.splitext(file.name)[1].lower()
            if ext not in ALLOWED_EXTENSIONS:
                raise forms.ValidationError(
                    f"Only PDF and image files are allowed ({', '.join(ALLOWED_EXTENSIONS)})."
                )
        return file


# ── Flight Logger Forms ────────────────────────────────────────────────────
from .models import FlightRecord, Pilot, Location
import json

class PreTakeoffForm(forms.Form):
    name             = forms.CharField(max_length=200, required=False,
                           widget=forms.TextInput(attrs={'placeholder': 'Optional flight name'}))
    aircraft         = forms.IntegerField(required=False, widget=forms.HiddenInput())
    aircraft_free    = forms.CharField(max_length=100, required=False,
                           widget=forms.TextInput(attrs={'placeholder': 'Enter registration'}))
    start_fuel       = forms.DecimalField(max_digits=7, decimal_places=1, min_value=0,
                           widget=forms.TextInput(attrs={'inputmode': 'decimal', 'placeholder': '0.0'}))
    departure        = forms.CharField(max_length=150,
                           widget=forms.TextInput(attrs={'placeholder': 'ICAO code or location name',
                                                         'list': 'location-list', 'autocomplete': 'off'}))
    destination      = forms.CharField(max_length=150,
                           widget=forms.TextInput(attrs={'placeholder': 'ICAO code or location name',
                                                         'list': 'location-list', 'autocomplete': 'off'}))
    vdo_start        = forms.DecimalField(max_digits=10, decimal_places=1, min_value=0,
                           widget=forms.TextInput(attrs={'inputmode': 'decimal', 'placeholder': '0.0'}))
    airswitch_start  = forms.DecimalField(max_digits=10, decimal_places=1, min_value=0,
                           widget=forms.TextInput(attrs={'inputmode': 'decimal', 'placeholder': '0.0'}))
    scheduled_departure_time = forms.DateTimeField(required=False,
                           widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    scheduled_arrival_time = forms.DateTimeField(required=False,
                           widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    pilot_in_command = forms.CharField(max_length=150,
                           widget=forms.TextInput(attrs={'list': 'pilot-list', 'autocomplete': 'off',
                                                         'placeholder': 'Select or type a name'}))
    additional_crew  = forms.CharField(required=False, widget=forms.HiddenInput())  # JSON list
    passenger_count  = forms.IntegerField(min_value=0,
                           widget=forms.NumberInput(attrs={'placeholder': '0'}))

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean(self):
        cleaned = super().clean()
        dep = cleaned.get('departure', '').strip()
        dest = cleaned.get('destination', '').strip()

        pic = cleaned.get('pilot_in_command', '').strip()
        try:
            crew = json.loads(cleaned.get('additional_crew') or '[]')
        except (json.JSONDecodeError, TypeError):
            crew = []
        if pic and pic in crew:
            self.add_error('pilot_in_command', 'Pilot in command cannot also be listed as additional crew.')
        cleaned['additional_crew'] = crew

        # VDO / Airswitch must be >= last recorded values
        if self.user:
            last = FlightRecord.objects.filter(
                user=self.user, status=FlightRecord.STATUS_COMPLETE
            ).order_by('-end_time').first()
            if last:
                vdo = cleaned.get('vdo_start')
                if vdo is not None and last.vdo_end is not None and vdo < last.vdo_end:
                    self.add_error('vdo_start',
                        f'VDO cannot go backwards (last recorded: {last.vdo_end}).')
                asw = cleaned.get('airswitch_start')
                if asw is not None and last.airswitch_end is not None and asw < last.airswitch_end:
                    self.add_error('airswitch_start',
                        f'Airswitch cannot go backwards (last recorded: {last.airswitch_end}).')
        return cleaned


class PostLandingForm(forms.Form):
    end_fuel           = forms.CharField(max_length=50,
                             widget=forms.TextInput(attrs={'inputmode': 'decimal', 'placeholder': '0.0 or "full"'}))
    fuel_added         = forms.DecimalField(max_digits=7, decimal_places=1, min_value=0, required=False,
                             widget=forms.TextInput(attrs={'inputmode': 'decimal', 'placeholder': '0.0'}))
    actual_destination = forms.CharField(max_length=150,
                             widget=forms.TextInput(attrs={'list': 'location-list', 'autocomplete': 'off',
                                                           'placeholder': 'ICAO code or location name'}))
    vdo_end            = forms.DecimalField(max_digits=10, decimal_places=1, min_value=0,
                             widget=forms.TextInput(attrs={'inputmode': 'decimal', 'placeholder': '0.0'}))
    airswitch_end      = forms.DecimalField(max_digits=10, decimal_places=1, min_value=0,
                             widget=forms.TextInput(attrs={'inputmode': 'decimal', 'placeholder': '0.0'}))
    notes              = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 4,
                             'placeholder': 'Any relevant notes…'}))

    def __init__(self, *args, flight=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.flight = flight

    def clean_end_fuel(self):
        val = self.cleaned_data.get('end_fuel')
        if val is None or val == '':
            raise forms.ValidationError('End fuel is required.')
        
        # Allow "full" only if aircraft is registered (not text input)
        if val.lower().strip() == 'full':
            if not self.flight or not self.flight.aircraft:
                raise forms.ValidationError('Cannot use "full" with a manually entered aircraft.')
            if not self.flight.aircraft.max_fuel:
                raise forms.ValidationError(f'Aircraft {self.flight.aircraft.registration} does not have a max fuel capacity set.')
            # Store the max_fuel value for later use
            self._end_fuel_value = self.flight.aircraft.max_fuel
            return val
        
        # Try to convert to decimal
        try:
            decimal_val = float(val)
            if decimal_val < 0:
                raise forms.ValidationError('End fuel cannot be negative.')
            self._end_fuel_value = decimal_val
            return val
        except (ValueError, TypeError):
            raise forms.ValidationError('End fuel must be a number or "full".')

    def clean_vdo_end(self):
        val = self.cleaned_data.get('vdo_end')
        if self.flight and val is not None and self.flight.vdo_start is not None:
            if val <= self.flight.vdo_start:
                raise forms.ValidationError(
                    f'VDO end must be greater than VDO start ({self.flight.vdo_start}).')
        return val

    def clean_airswitch_end(self):
        val = self.cleaned_data.get('airswitch_end')
        if self.flight and val is not None and self.flight.airswitch_start is not None:
            if val <= self.flight.airswitch_start:
                raise forms.ValidationError(
                    f'Airswitch end must be greater than Airswitch start ({self.flight.airswitch_start}).')
        return val


class FlightAnnotationForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea(attrs={'rows': 3,
                               'placeholder': 'Add an annotation to this flight record…'}))
