from django.db import models

from patients.models import Patient
from appointments.models import Appointment

# Create your models here.
class TherapySession(models.Model):
    MOOD_CHOICES = [
        ("very_bad", "Muito mal"),
        ("bad", "Mal"),
        ("neutral", "Neutro"),
        ("good", "Bem"),
        ("very_good", "Muito bem"),
    ]

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="therapy_sessions"
    )

    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="therapy_session"
    )

    session_date = models.DateTimeField()

    summary = models.TextField(
        help_text="Resumo da sessão"
    )

    homework = models.TextField(
        blank=True,
        null=True
    )

    evolution_notes = models.TextField(blank=True, null=True)

    patient_mood = models.CharField(
        max_length=20,
        choices=MOOD_CHOICES,
        blank=True,
        null=True
    )

    next_steps = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sessão de {self.patient.full_name} - {self.session_date}"