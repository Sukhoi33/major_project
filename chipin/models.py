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
