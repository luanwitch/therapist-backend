from rest_framework import viewsets
from .models import Patient
from .serializers import PatientSerializer


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.none()
    serializer_class = PatientSerializer
    search_fields = ["full_name", "email", "phone"]
    ordering_fields = ["full_name", "created_at"]
    filterset_fields = ["active"]

    def get_queryset(self):
        return Patient.objects.filter(therapist=self.request.user).order_by("full_name")

    def perform_create(self, serializer):
        serializer.save(therapist=self.request.user)