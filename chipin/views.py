from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django_otp import devices_for_user
from django_otp.decorators import otp_required

from .models import Aircraft
from .forms import AircraftForm


def landing(request):
    """Landing page shown to unauthenticated users."""
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

    context = {
        "has_device": has_device,
        "is_verified": is_verified,
        "user": request.user,
    }
    return render(request, 'chipin/home.html', context)


@login_required
def aircraft_profiles(request):
    """List all aircraft belonging to the logged-in user."""
    aircraft_list = Aircraft.objects.filter(user=request.user)
    return render(request, 'chipin/aircraft_profiles.html', {'aircraft_list': aircraft_list})


@login_required
def add_aircraft(request):
    """Add a new aircraft profile."""
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
def edit_aircraft(request, pk):
    """Edit an existing aircraft profile (must belong to the logged-in user)."""
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
    """Delete an aircraft profile (must belong to the logged-in user)."""
    aircraft = get_object_or_404(Aircraft, pk=pk, user=request.user)
    aircraft.delete()
    return redirect('chipin:aircraft_profiles')


@login_required
def new_flight(request):
    """New Flight page."""
    context = {"user": request.user}
    return render(request, 'chipin/new_flight.html', context)


@login_required
def flight_log(request):
    """Flight Log page."""
    context = {"user": request.user}
    return render(request, 'chipin/flight_log.html', context)
