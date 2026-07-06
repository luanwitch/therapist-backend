from django.db import models
from patients.models import Patient


class Appointment(models.Model):
    STATUS_CHOICES = [
        ("scheduled", "Agendado"),
        ("confirmed", "Confirmado"),
        ("cancelled", "Cancelado"),
        ("completed", "Realizado"),
        ("no_show", "Faltou"),
    ]

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="appointments"
    )

    schedule_at = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=50)

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="scheduled"
    )

    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient.full_name} - {self.schedule_at}"