from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import os


class Aircraft(models.Model):
    FUEL_UNIT_CHOICES = [
        ('L/hr', 'L/hr'),
        ('gal/hr', 'gal/hr'),
    ]
    SPEED_UNIT_CHOICES = [
        ('kts', 'kts'),
        ('km/h', 'km/h'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='aircraft')
    registration = models.CharField(max_length=20)
    model = models.CharField(max_length=100)
    fuel_consumption = models.DecimalField(max_digits=7, decimal_places=1)
    fuel_unit = models.CharField(max_length=10, choices=FUEL_UNIT_CHOICES, default='L/hr')
    speed_unit = models.CharField(max_length=10, choices=SPEED_UNIT_CHOICES, default='kts')

    vso = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)
    vs1 = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)
    vr  = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)
    vx  = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)
    vy  = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)
    vfe = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)
    vno = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)
    vne = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)
    va  = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)
    vlo = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)
    vle = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['registration']

    def __str__(self):
        return f"{self.registration} ({self.model})"


def aircraft_document_upload_path(instance, filename):
    """Upload to: aircraft_docs/<user_id>/<aircraft_id>/<doc_type>/<filename>"""
    return f"aircraft_docs/{instance.aircraft.user.id}/{instance.aircraft.id}/{instance.doc_type}/{filename}"


class AircraftDocument(models.Model):
    DOC_TYPE_CHOICES = [
        ('checklist', 'Checklist'),
        ('maintenance', 'Maintenance Release'),
        ('manual', 'Manual'),
    ]

    aircraft = models.ForeignKey(Aircraft, on_delete=models.CASCADE, related_name='documents')
    doc_type = models.CharField(max_length=20, choices=DOC_TYPE_CHOICES)
    name = models.CharField(max_length=200)
    file = models.FileField(upload_to=aircraft_document_upload_path)
    uploaded_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_doc_type_display()}) — {self.aircraft.registration}"

    def filename(self):
        return os.path.basename(self.file.name)

    def is_pdf(self):
        return self.file.name.lower().endswith('.pdf')


# ── Flight Logger ──────────────────────────────────────────────────────────

class Pilot(models.Model):
    """Reusable pilot name pool per user."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pilots')
    name = models.CharField(max_length=150)

    class Meta:
        ordering = ['name']
        unique_together = [('user', 'name')]

    def __str__(self):
        return self.name


class Location(models.Model):
    """Saved/recent locations per user."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='locations')
    code = models.CharField(max_length=150)

    class Meta:
        ordering = ['code']
        unique_together = [('user', 'code')]

    def __str__(self):
        return self.code


class FlightRecord(models.Model):
    STATUS_PRETAKEOFF = 'pretakeoff'
    STATUS_INFLIGHT   = 'inflight'
    STATUS_COMPLETE   = 'complete'
    STATUS_CHOICES = [
        (STATUS_PRETAKEOFF, 'Pre-Takeoff'),
        (STATUS_INFLIGHT,   'In Flight'),
        (STATUS_COMPLETE,   'Complete'),
    ]

    user   = models.ForeignKey(User, on_delete=models.CASCADE, related_name='flights')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PRETAKEOFF)

    # ── Pre-takeoff ────────────────────────────────────────────────────────
    name              = models.CharField(max_length=200, blank=True)
    aircraft          = models.ForeignKey(Aircraft, on_delete=models.SET_NULL, null=True, blank=True)
    aircraft_free     = models.CharField(max_length=100, blank=True)   # fallback if no registered aircraft

    start_time        = models.DateTimeField(null=True, blank=True)    # auto-set on submission
    scheduled_departure_time = models.DateTimeField(null=True, blank=True)  # user-entered scheduled departure
    scheduled_arrival_time   = models.DateTimeField(null=True, blank=True)  # user-entered scheduled arrival
    start_fuel        = models.DecimalField(max_digits=7, decimal_places=1, null=True, blank=True)
    fuel_unit         = models.CharField(max_length=10, blank=True, default='L')

    departure         = models.CharField(max_length=150, blank=True)
    destination       = models.CharField(max_length=150, blank=True)

    vdo_start         = models.DecimalField(max_digits=10, decimal_places=1, null=True, blank=True)
    airswitch_start   = models.DecimalField(max_digits=10, decimal_places=1, null=True, blank=True)

    pilot_in_command  = models.CharField(max_length=150, blank=True)
    additional_crew   = models.JSONField(default=list, blank=True)    # list of names
    passenger_count   = models.IntegerField(null=True, blank=True)

    # ── Post-landing ───────────────────────────────────────────────────────
    end_time          = models.DateTimeField(null=True, blank=True)
    end_fuel          = models.DecimalField(max_digits=7, decimal_places=1, null=True, blank=True)
    fuel_added        = models.DecimalField(max_digits=7, decimal_places=1, null=True, blank=True)  # fuel added between start and end
    actual_destination = models.CharField(max_length=150, blank=True)
    vdo_end           = models.DecimalField(max_digits=10, decimal_places=1, null=True, blank=True)
    airswitch_end     = models.DecimalField(max_digits=10, decimal_places=1, null=True, blank=True)
    notes             = models.TextField(blank=True)

    created_at        = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-start_time', '-created_at']

    def __str__(self):
        name = self.name or 'Unnamed Flight'
        return f"{name} ({self.departure} → {self.actual_destination or self.destination})"

    def display_name(self):
        return self.name if self.name else 'Unnamed Flight'

    @property
    def vdo_total(self):
        if self.vdo_end is not None and self.vdo_start is not None:
            return self.vdo_end - self.vdo_start
        return None

    @property
    def airswitch_total(self):
        if self.airswitch_end is not None and self.airswitch_start is not None:
            return self.airswitch_end - self.airswitch_start
        return None

    @property
    def fuel_used(self):
        if self.end_fuel is not None and self.start_fuel is not None:
            return self.start_fuel - self.end_fuel
        return None


class FlightAnnotation(models.Model):
    """Post-submission notes attached to a completed, locked flight record."""
    flight    = models.ForeignKey(FlightRecord, on_delete=models.CASCADE, related_name='annotations')
    author    = models.ForeignKey(User, on_delete=models.CASCADE)
    text      = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['created_at']
