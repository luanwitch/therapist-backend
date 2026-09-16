from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from patients.models import Patient
from appointments.models import Appointment
from finances.models import Payment


class AppointmentAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.client.force_authenticate(user=self.user)
        self.patient = Patient.objects.create(
            full_name="Paciente Teste",
            email="paciente@teste.com",
            phone="11999999999",
        )

    def test_create_appointment_success(self):
        future_date = timezone.now() + timedelta(days=2)
        payload = {
            "patient": self.patient.id,
            "schedule_at": future_date.isoformat(),
            "duration_minutes": 50,
            "price": "180.00",
            "status": "scheduled",
        }
        response = self.client.post("/api/appointments/", payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Appointment.objects.count(), 1)

        # Pagamento gerado automaticamente como pendente
        payment = Payment.objects.filter(appointment_id=response.data["id"]).first()
        self.assertIsNotNone(payment)
        self.assertEqual(payment.status, "pending")
        self.assertEqual(float(payment.amount), 180.00)

    def test_create_appointment_in_past_rejected(self):
        past_date = timezone.now() - timedelta(days=2)
        payload = {
            "patient": self.patient.id,
            "schedule_at": past_date.isoformat(),
            "duration_minutes": 50,
            "price": "180.00",
            "status": "scheduled",
        }
        response = self.client.post("/api/appointments/", payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_past_appointment_status_succeeds(self):
        # Consulta existente com data no passado (como appointment 5 e 6)
        past_date = timezone.now() - timedelta(days=5)
        appointment = Appointment.objects.create(
            patient=self.patient,
            schedule_at=past_date,
            duration_minutes=50,
            price=180.00,
            status="scheduled",
        )

        # Atualização para 'completed' com schedule_at original deve funcionar
        response = self.client.patch(
            f"/api/appointments/{appointment.id}/",
            {
                "schedule_at": appointment.schedule_at.isoformat(),
                "status": "completed",
                "notes": "Sessão concluída com sucesso",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, "completed")
        self.assertEqual(appointment.notes, "Sessão concluída com sucesso")

    def test_cancelling_appointment_cancels_pending_payment(self):
        future_date = timezone.now() + timedelta(days=1)
        appointment = Appointment.objects.create(
            patient=self.patient,
            schedule_at=future_date,
            duration_minutes=50,
            price=200.00,
            status="scheduled",
        )
        payment = Payment.objects.create(
            patient=self.patient,
            appointment=appointment,
            amount=200.00,
            status="pending",
        )

        response = self.client.patch(
            f"/api/appointments/{appointment.id}/",
            {"status": "cancelled"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        payment.refresh_from_db()
        self.assertEqual(payment.status, "cancelled")
