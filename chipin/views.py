from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.utils import timezone as tz
from django_otp import devices_for_user
from django_otp.decorators import otp_required
import json

from .models import Aircraft, AircraftDocument, FlightRecord, Pilot, Location
from .forms import AircraftForm, AircraftDocumentForm, PreTakeoffForm, PostLandingForm


def landing(request):
    if request.user.is_authenticated:
        return redirect('chipin:home')
    return render(request, 'chipin/landing.html')


@otp_required
def sensitive_area(request):
    return render(request, "chipin/sensitive.html")


@login_required
def home(request):
    has_device = any(devices_for_user(request.user, for_verify=True))
    is_verified = False
    if hasattr(request.user, "is_verified"):
        try:
            is_verified = bool(request.user.is_verified())
        except TypeError:
            is_verified = bool(request.user.is_verified)
    return render(request, 'chipin/home.html', {
        "has_device": has_device,
        "is_verified": is_verified,
        "user": request.user,
    })


@login_required
def aircraft_profiles(request):
    aircraft_list = Aircraft.objects.filter(user=request.user)
    return render(request, 'chipin/aircraft_profiles.html', {'aircraft_list': aircraft_list})


@login_required
def add_aircraft(request):
    if request.method == 'POST':
        form = AircraftForm(request.POST)
        if form.is_valid():
            aircraft = form.save(commit=False)
            aircraft.user = request.user
            aircraft.save()
            return redirect('chipin:aircraft_profiles')
    else:
        form = AircraftForm()
    return render(request, 'chipin/add_aircraft.html', {'form': form})


@login_required
def view_aircraft(request, pk):
    aircraft = get_object_or_404(Aircraft, pk=pk, user=request.user)
    return render(request, 'chipin/view_aircraft.html', {'aircraft': aircraft})


@login_required
def edit_aircraft(request, pk):
    aircraft = get_object_or_404(Aircraft, pk=pk, user=request.user)
    if request.method == 'POST':
        form = AircraftForm(request.POST, instance=aircraft)
        if form.is_valid():
            form.save()
            return redirect('chipin:aircraft_profiles')
    else:
        form = AircraftForm(instance=aircraft)
    return render(request, 'chipin/edit_aircraft.html', {'form': form, 'aircraft': aircraft})


@login_required
@require_POST
def delete_aircraft(request, pk):
    aircraft = get_object_or_404(Aircraft, pk=pk, user=request.user)
    aircraft.delete()
    return redirect('chipin:aircraft_profiles')


# ── Document views ──────────────────────────────────────────────────────────

DOC_TYPE_CONFIG = {
    'checklist': {
        'label': 'Checklist',
        'label_plural': 'Checklists',
        'list_template': 'chipin/checklists.html',
        'add_template': 'chipin/add_checklist.html',
    },
    'maintenance': {
        'label': 'Maintenance Release',
        'label_plural': 'Maintenance Releases',
        'list_template': 'chipin/maintenances.html',
        'add_template': 'chipin/add_maintenance.html',
    },
    'manual': {
        'label': 'Manual',
        'label_plural': 'Manuals',
        'list_template': 'chipin/manuals.html',
        'add_template': 'chipin/add_manual.html',
    },
}


@login_required
def document_list(request, pk, doc_type):
    aircraft = get_object_or_404(Aircraft, pk=pk, user=request.user)
    config = DOC_TYPE_CONFIG[doc_type]
    documents = aircraft.documents.filter(doc_type=doc_type)
    return render(request, config['list_template'], {
        'aircraft': aircraft,
        'documents': documents,
        'doc_type': doc_type,
        'config': config,
    })


@login_required
def add_document(request, pk, doc_type):
    aircraft = get_object_or_404(Aircraft, pk=pk, user=request.user)
    config = DOC_TYPE_CONFIG[doc_type]
    if request.method == 'POST':
        form = AircraftDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.aircraft = aircraft
            doc.doc_type = doc_type
            doc.save()
            return redirect('chipin:document_list', pk=pk, doc_type=doc_type)
    else:
        form = AircraftDocumentForm()
    return render(request, config['add_template'], {
        'aircraft': aircraft,
        'form': form,
        'doc_type': doc_type,
        'config': config,
    })


@login_required
@require_POST
def delete_document(request, pk, doc_type, doc_pk):
    aircraft = get_object_or_404(Aircraft, pk=pk, user=request.user)
    doc = get_object_or_404(AircraftDocument, pk=doc_pk, aircraft=aircraft, doc_type=doc_type)
    doc.file.delete(save=False)
    doc.delete()
    return redirect('chipin:document_list', pk=pk, doc_type=doc_type)


# ── Flight Logger Views ─────────────────────────────────────────────────────

def _save_pilot(user, name):
    name = name.strip()
    if name:
        Pilot.objects.get_or_create(user=user, name=name)


def _save_location(user, code):
    code = code.strip()
    if code:
        Location.objects.get_or_create(user=user, code=code)


@login_required
def new_flight(request):
    """Pre-takeoff form."""
    incomplete = FlightRecord.objects.filter(
        user=request.user, status=FlightRecord.STATUS_INFLIGHT
    ).first()

    aircraft_list = Aircraft.objects.filter(user=request.user)
    pilots        = Pilot.objects.filter(user=request.user)
    locations     = Location.objects.filter(user=request.user)

    if request.method == 'POST':
        form = PreTakeoffForm(request.POST, user=request.user)
        if form.is_valid():
            d = form.cleaned_data
            flight = FlightRecord(
                user             = request.user,
                status           = FlightRecord.STATUS_INFLIGHT,
                name             = d['name'],
                start_time       = tz.now(),
                scheduled_departure_time = d.get('scheduled_departure_time'),
                scheduled_arrival_time   = d.get('scheduled_arrival_time'),
                start_fuel       = d['start_fuel'],
                departure        = d['departure'].strip().upper(),
                destination      = d['destination'].strip().upper(),
                vdo_start        = d['vdo_start'],
                airswitch_start  = d['airswitch_start'],
                pilot_in_command = d['pilot_in_command'].strip(),
                additional_crew  = d['additional_crew'],
                passenger_count  = d['passenger_count'],
            )
            ac_pk = d.get('aircraft')
            if ac_pk:
                try:
                    flight.aircraft = Aircraft.objects.get(pk=ac_pk, user=request.user)
                    flight.fuel_unit = flight.aircraft.fuel_unit
                except Aircraft.DoesNotExist:
                    pass
            else:
                flight.aircraft_free = d.get('aircraft_free', '').strip()
            flight.save()

            _save_pilot(request.user, d['pilot_in_command'])
            for crew in d['additional_crew']:
                _save_pilot(request.user, crew)
            _save_location(request.user, d['departure'])
            _save_location(request.user, d['destination'])

            return redirect('chipin:current_flight', pk=flight.pk)
    else:
        form = PreTakeoffForm(user=request.user)

    return render(request, 'chipin/new_flight.html', {
        'form': form,
        'incomplete': incomplete,
        'aircraft_list': aircraft_list,
        'pilots': pilots,
        'locations': locations,
    })


@login_required
def edit_flight(request, pk):
    """Edit an in-flight flight's pre-takeoff details."""
    flight = get_object_or_404(FlightRecord, pk=pk, user=request.user,
                               status=FlightRecord.STATUS_INFLIGHT)
    
    aircraft_list = Aircraft.objects.filter(user=request.user)
    pilots        = Pilot.objects.filter(user=request.user)
    locations     = Location.objects.filter(user=request.user)

    if request.method == 'POST':
        form = PreTakeoffForm(request.POST, user=request.user)
        if form.is_valid():
            d = form.cleaned_data
            flight.name             = d['name']
            flight.scheduled_departure_time = d.get('scheduled_departure_time')
            flight.scheduled_arrival_time   = d.get('scheduled_arrival_time')
            flight.start_fuel       = d['start_fuel']
            flight.departure        = d['departure'].strip().upper()
            flight.destination      = d['destination'].strip().upper()
            flight.vdo_start        = d['vdo_start']
            flight.airswitch_start  = d['airswitch_start']
            flight.pilot_in_command = d['pilot_in_command'].strip()
            flight.additional_crew  = d['additional_crew']
            flight.passenger_count  = d['passenger_count']
            
            ac_pk = d.get('aircraft')
            if ac_pk:
                try:
                    flight.aircraft = Aircraft.objects.get(pk=ac_pk, user=request.user)
                    flight.fuel_unit = flight.aircraft.fuel_unit
                except Aircraft.DoesNotExist:
                    pass
            else:
                flight.aircraft_free = d.get('aircraft_free', '').strip()
            flight.save()

            _save_pilot(request.user, d['pilot_in_command'])
            for crew in d['additional_crew']:
                _save_pilot(request.user, crew)
            _save_location(request.user, d['departure'])
            _save_location(request.user, d['destination'])

            return redirect('chipin:current_flight', pk=flight.pk)
    else:
        # Pre-populate form with existing flight data
        initial_data = {
            'name': flight.name,
            'aircraft': flight.aircraft.pk if flight.aircraft else '',
            'aircraft_free': flight.aircraft_free,
            'start_fuel': flight.start_fuel,
            'departure': flight.departure,
            'destination': flight.destination,
            'vdo_start': flight.vdo_start,
            'airswitch_start': flight.airswitch_start,
            'pilot_in_command': flight.pilot_in_command,
            'additional_crew': json.dumps(flight.additional_crew) if flight.additional_crew else '[]',
            'passenger_count': flight.passenger_count,
            'scheduled_departure_time': flight.scheduled_departure_time,
            'scheduled_arrival_time': flight.scheduled_arrival_time,
        }
        form = PreTakeoffForm(user=request.user, initial=initial_data)

    return render(request, 'chipin/new_flight.html', {
        'form': form,
        'aircraft_list': aircraft_list,
        'pilots': pilots,
        'locations': locations,
        'flight': flight,
        'is_edit': True,
    })


@login_required
def current_flight(request, pk):
    """In-flight screen - confirmation page."""
    flight = get_object_or_404(FlightRecord, pk=pk, user=request.user,
                               status=FlightRecord.STATUS_INFLIGHT)
    return render(request, 'chipin/current_flight.html', {'flight': flight})


@login_required
def current_flight_taf(request, pk):
    """In-flight screen - TAF data page."""
    flight = get_object_or_404(FlightRecord, pk=pk, user=request.user,
                               status=FlightRecord.STATUS_INFLIGHT)
    # TODO: Fetch actual TAF and frequency data
    context = {
        'flight': flight,
        'taf_departure': None,
        'taf_destination': None,
        'frequencies_departure': [],
        'frequencies_destination': [],
    }
    return render(request, 'chipin/current_flight_taf.html', context)


@login_required
def current_flight_live(request, pk):
    """In-flight screen - live TAF page."""
    flight = get_object_or_404(FlightRecord, pk=pk, user=request.user,
                               status=FlightRecord.STATUS_INFLIGHT)
    # TODO: Fetch actual live TAF and frequency data
    context = {
        'flight': flight,
        'live_taf': None,
        'frequencies_departure': [],
        'frequencies_destination': [],
    }
    return render(request, 'chipin/current_flight_live.html', context)


@login_required
def post_landing(request, pk):
    """Post-landing form."""
    flight = get_object_or_404(FlightRecord, pk=pk, user=request.user,
                               status=FlightRecord.STATUS_INFLIGHT)
    locations = Location.objects.filter(user=request.user)

    if request.method == 'POST':
        form = PostLandingForm(request.POST, flight=flight)
        if form.is_valid():
            d = form.cleaned_data
            flight.end_time           = tz.now()
            
            # Handle end_fuel - convert "full" to max_fuel value
            end_fuel_value = form._end_fuel_value
            flight.end_fuel           = end_fuel_value
            
            flight.fuel_added         = d.get('fuel_added')
            flight.actual_destination = d['actual_destination'].strip().upper()
            flight.vdo_end            = d['vdo_end']
            flight.airswitch_end      = d['airswitch_end']
            flight.notes              = d['notes']
            flight.status             = FlightRecord.STATUS_COMPLETE
            flight.save()

            _save_location(request.user, d['actual_destination'])
            return redirect('chipin:flight_summary', pk=flight.pk)
    else:
        form = PostLandingForm(flight=flight,
                               initial={'actual_destination': flight.destination})

    return render(request, 'chipin/post_landing.html', {
        'form': form,
        'flight': flight,
        'locations': locations,
    })


@login_required
def flight_summary(request, pk):
    """Read-only summary of a completed flight."""
    flight = get_object_or_404(FlightRecord, pk=pk, user=request.user,
                               status=FlightRecord.STATUS_COMPLETE)
    return render(request, 'chipin/flight_summary.html', {'flight': flight})


@login_required
@require_POST
def delete_flight(request, pk):
    """Delete a flight record (for testing purposes)."""
    flight = get_object_or_404(FlightRecord, pk=pk, user=request.user)
    flight.delete()
    return redirect('chipin:flight_log')


@login_required
def flight_log(request):
    """Chronological list of all completed flights."""
    flights = FlightRecord.objects.filter(
        user=request.user, status=FlightRecord.STATUS_COMPLETE
    )
    return render(request, 'chipin/flight_log.html', {'flights': flights})
