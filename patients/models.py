from django.db import models

# Create your models here.
class Patient(models.Model):
    full_name = models.CharField(max_length=150)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    birth_date = models.DateField(blank=20, null=True)

    emergency_contact_name = models.CharField(max_length=150, blank = True, null = True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True, null= True)

    notes = models.TextField(default=True)

    active = models.BooleanField(default=True)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.full_name




