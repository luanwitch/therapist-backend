from rest_framework import viewsets, status
from rest_framework.response import Response
from finances.models import Payment

from .models import Appointment
from .serializers import AppointmentSerializer

#Viewset
class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.none()
    serializer_class = AppointmentSerializer

    #filtroset_fields
    search_fields = ["patient__full_name", "notes"]
    ordering_fields = ["schedule_at", "created_at"]
    filterset_fields = ["status", "patient"]

    def get_queryset(self):
        return (
            Appointment.objects.filter(patient__therapist=self.request.user)
            .select_related("patient")
            .order_by("schedule_at")
        )

    #Não permitir dois agendamentos no mesmo horário regra de negócio (por terapeuta).
    def create(self, request, *args, **kwargs):
        schedule_at = request.data.get("schedule_at")

        if schedule_at and Appointment.objects.filter(
            patient__therapist=request.user,
            schedule_at=schedule_at
        ).exists():
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

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        schedule_at = request.data.get("schedule_at")

        if schedule_at:
            exists = Appointment.objects.filter(
                patient__therapist=request.user,
                schedule_at=schedule_at
            ).exclude(id=instance.id).exists()

            if exists:
                return Response(
                    {"detail": "Já existe um agendamento neste horário."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return super().update(request, *args, **kwargs)

    def perform_update(self, serializer):
        appointment = serializer.save()
        if appointment.status == "cancelled":
            try:
                payment = appointment.payment
                if payment and payment.status == "pending":
                    payment.status = "cancelled"
                    payment.save(update_fields=["status"])
            except Exception:
                pass

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            payment = instance.payment
            if payment and payment.status == "pending":
                payment.delete()
        except Exception:
            pass
        return super().destroy(request, *args, **kwargs)