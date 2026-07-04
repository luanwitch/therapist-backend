from rest_framework import viewsets, status
from rest_framework.response import Response
from finances.models import Payment

from .models import Appointment
from .serializers import AppointmentSerializer

#Viewset
class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

    #filtroset_fields
    search_fields = ["patient__full_name", "notes"]
    ordering_fields = ["schedule_at", "created_at"]
    filterset_fields = ["status", "patient"]

    #Não permitir dois agendamentos no mesmo horário.
    def create(self, request, *args, **kwargs):
        schedule_at = request.data.get("schedule_at")

        if Appointment.objects.filter(schedule_at=schedule_at).exists():
            return Response(
                {
                    "error": "Já existe um agendamento neste horário."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        appointment = serializer.save()

        Payment.objects.create(
            patient=appointment.patient,
            appointment=appointment,
            amount=appointment.price,
            status="pending"
        )

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )