from rest_framework import serializers
from .models import Patient

class PatientSerializer(serializers.ModelSerializer):
    therapist = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Patient
        fields = "__all__"