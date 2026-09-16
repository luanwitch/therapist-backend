from rest_framework import serializers
from patients.models import Patient
from appointments.models import Appointment
from .models import TherapySession

class TherapySessionSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and hasattr(request, "user") and request.user.is_authenticated:
            self.fields["patient"].queryset = Patient.objects.filter(therapist=request.user)
            self.fields["appointment"].queryset = Appointment.objects.filter(patient__therapist=request.user)

    class Meta:
        model = TherapySession
        fields = "__all__"