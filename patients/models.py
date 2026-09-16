from django.db import models
from django.contrib.auth.models import User

class Patient(models.Model):
    therapist = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="patients",
    )
    full_name = models.CharField(max_length=150)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)

    emergency_contact_name = models.CharField(max_length=150, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True, null=True)

    notes = models.TextField(blank=True, default="")

    active = models.BooleanField(default=True)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.full_name
