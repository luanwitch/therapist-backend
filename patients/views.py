from django.shortcuts import render
from rest_framework import viewsets
from .models import Patient
from .serializers import PatientSerializer


# Create your views here.
class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    #Na views quando queremos proteger uma única view no settings quando queremos proteger toda a API.
    #permission_classes = [IsAuthenticated]
    
    search_fields = ["full_name", "email", "phone"]
    ordering_fields = ["full_name", "created_at"]
    filterset_fields = ["active"]