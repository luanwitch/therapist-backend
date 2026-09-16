from rest_framework import serializers
from django.utils import timezone
from patients.models import Patient
from .models import Appointment

class AppointmentSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(
        source="patient.full_name",
        read_only=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and hasattr(request, "user") and request.user.is_authenticated:
            self.fields["patient"].queryset = Patient.objects.filter(therapist=request.user)

    def validate_schedule_at(self, value):
        # Se for uma atualização e o horário não tiver sido alterado, permite manter
        if self.instance and self.instance.schedule_at == value:
            return value

        # Na criação de novo agendamento, não permitir agendar no passado
        if not self.instance and value < timezone.now():
            raise serializers.ValidationError(
                "Não é possível agendar novas consultas em horários que já passaram."
            )
        return value

    class Meta:
        model = Appointment
        fields = "__all__"