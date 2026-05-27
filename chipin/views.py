from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django_otp import devices_for_user
from django_otp.decorators import otp_required

from .models import Aircraft, AircraftDocument
from .forms import AircraftForm, AircraftDocumentForm


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


# ── Document views (shared logic for checklists, maintenance, manuals) ──

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
    doc.file.delete(save=False)  # delete the actual file from storage
    doc.delete()
    return redirect('chipin:document_list', pk=pk, doc_type=doc_type)


@login_required
def new_flight(request):
    return render(request, 'chipin/new_flight.html', {"user": request.user})


@login_required
def flight_log(request):
    return render(request, 'chipin/flight_log.html', {"user": request.user})
