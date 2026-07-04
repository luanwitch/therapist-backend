from rest_framework import viewsets, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from appointments.models import Appointment

from .models import TherapySession
from .serializers import TherapySessionSerializer


class TherapySessionViewSet(viewsets.ModelViewSet):
    queryset = TherapySession.objects.all()
    serializer_class = TherapySessionSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["patient__full_name", "summary", "evolution_notes"]
    ordering_fields = ["session_date", "created_at"]
    filterset_fields = ["patient", "patient_mood"]

    def create(self, request, *args, **kwargs):
        appointment_id = request.data.get("appointment")
        patient_id = request.data.get("patient")

        if appointment_id:
            try:
                appointment = Appointment.objects.get(id=appointment_id)
            except Appointment.DoesNotExist:
                return Response(
                    {"error": "Agendamento não encontrado."},
                    status=status.HTTP_404_NOT_FOUND
                )

            if TherapySession.objects.filter(appointment_id=appointment_id).exists():
                return Response(
                    {"error": "Este agendamento já possui uma sessão."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if patient_id and appointment.patient_id != int(patient_id):
                return Response(
                    {"error": "O paciente da sessão deve ser o mesmo do agendamento."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )