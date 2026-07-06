from rest_framework import serializers
from django.utils import timezone
from .models import Appointment

class AppointmentSerializer(serializers.ModelSerializer):
    #FullCalendar: 
    patient_name = serializers.CharField(
        source="patient.full_name",
        read_only=True
    )

    def validate_schedule_at(self, value):
        if value < timezone.now():
            raise serializers.ValidationError(
                "Não é possível agendar consultas em horários que já passaram."
            )
        return value
        
    class Meta:
        model = Appointment
        fields = "__all__"