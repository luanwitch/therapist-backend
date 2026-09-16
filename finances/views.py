from django.shortcuts import render
from rest_framework import viewsets
from .models import Payment
from .serializers import PaymentSerializer

# Create your views here.
class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.none()
    serializer_class = PaymentSerializer

    search_fields = ["patient__full_name", "notes"]
    ordering_fields = ["due_date", "paid_at", "amount", "created_at"]
    filterset_fields = ["status", "payment_method", "patient"]

    def get_queryset(self):
        return (
            Payment.objects.filter(patient__therapist=self.request.user)
            .select_related("patient", "appointment")
            .order_by("-due_date")
        )