from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


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

    # V-speeds (all optional — not every aircraft type has all of them)
    vso = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)  # Stall, landing config
    vs1 = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)  # Stall, clean
    vr  = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)  # Rotation
    vx  = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)  # Best angle of climb
    vy  = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)  # Best rate of climb
    vfe = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)  # Max flap extended
    vno = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)  # Max structural cruising
    vne = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)  # Never exceed
    va  = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)  # Manoeuvring
    vlo = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)  # Max gear operating
    vle = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)  # Max gear extended

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['registration']

    def __str__(self):
        return f"{self.registration} ({self.model})"
