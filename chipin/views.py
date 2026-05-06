from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django_otp import devices_for_user
from django_otp.decorators import otp_required  


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
    """Aircraft Profiles page."""
    context = {"user": request.user}
    return render(request, 'chipin/aircraft_profiles.html', context)


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
