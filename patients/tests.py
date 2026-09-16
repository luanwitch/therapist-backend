from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from patients.models import Patient
from appointments.models import Appointment
from therapy_sessions.models import TherapySession
from finances.models import Payment


class MultiTenantIsolationTests(APITestCase):
    def setUp(self):
        # Cria dois terapeutas distintos
        self.therapist_a = User.objects.create_user(username="therapist_a", password="password123")
        self.therapist_b = User.objects.create_user(username="therapist_b", password="password123")

        # Dados do terapeuta A
        self.patient_a = Patient.objects.create(
            full_name="Paciente A",
            email="paciente_a@example.com",
            phone="11911111111",
            therapist=self.therapist_a,
        )
        self.future_date = timezone.now() + timedelta(days=3)
        self.appointment_a = Appointment.objects.create(
            patient=self.patient_a,
            schedule_at=self.future_date,
            duration_minutes=50,
            price="200.00",
            status="scheduled",
        )
        self.session_a = TherapySession.objects.create(
            patient=self.patient_a,
            appointment=self.appointment_a,
            session_date=self.future_date,
            summary="Sessão clínica do terapeuta A",
        )
        self.payment_a = Payment.objects.create(
            patient=self.patient_a,
            appointment=self.appointment_a,
            amount="200.00",
            status="pending",
        )

        # Dados do terapeuta B
        self.patient_b = Patient.objects.create(
            full_name="Paciente B",
            email="paciente_b@example.com",
            phone="11922222222",
            therapist=self.therapist_b,
        )
        self.appointment_b = Appointment.objects.create(
            patient=self.patient_b,
            schedule_at=self.future_date,  # Mesmo horário propositalmente
            duration_minutes=50,
            price="250.00",
            status="scheduled",
        )
        self.session_b = TherapySession.objects.create(
            patient=self.patient_b,
            appointment=self.appointment_b,
            session_date=self.future_date,
            summary="Sessão clínica do terapeuta B",
        )
        self.payment_b = Payment.objects.create(
            patient=self.patient_b,
            appointment=self.appointment_b,
            amount="250.00",
            status="pending",
        )

    # ------------------ PATIENTS ISOLATION ------------------

    def test_therapist_lists_only_own_patients(self):
        self.client.force_authenticate(user=self.therapist_a)
        response = self.client.get("/api/patients/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get("results", response.data)
        patient_ids = [p["id"] for p in results]
        self.assertIn(self.patient_a.id, patient_ids)
        self.assertNotIn(self.patient_b.id, patient_ids)

    def test_therapist_cannot_access_other_patient_detail(self):
        self.client.force_authenticate(user=self.therapist_a)
        response = self.client.get(f"/api/patients/{self.patient_b.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_therapist_cannot_update_other_patient(self):
        self.client.force_authenticate(user=self.therapist_a)
        response = self.client.patch(
            f"/api/patients/{self.patient_b.id}/",
            {"full_name": "Nome Alterado Indevidamente"},
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.patient_b.refresh_from_db()
        self.assertEqual(self.patient_b.full_name, "Paciente B")

    def test_therapist_cannot_delete_other_patient(self):
        self.client.force_authenticate(user=self.therapist_a)
        response = self.client.delete(f"/api/patients/{self.patient_b.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Patient.objects.filter(id=self.patient_b.id).exists())

    def test_created_patient_automatically_assigned_to_authenticated_therapist(self):
        self.client.force_authenticate(user=self.therapist_a)
        payload = {
            "full_name": "Novo Paciente A",
            "email": "novo@example.com",
            "phone": "11988887777",
        }
        response = self.client.post("/api/patients/", payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_patient = Patient.objects.get(id=response.data["id"])
        self.assertEqual(new_patient.therapist, self.therapist_a)

    # ------------------ APPOINTMENTS ISOLATION ------------------

    def test_therapist_lists_only_own_appointments(self):
        self.client.force_authenticate(user=self.therapist_a)
        response = self.client.get("/api/appointments/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get("results", response.data)
        appt_ids = [a["id"] for a in results]
        self.assertIn(self.appointment_a.id, appt_ids)
        self.assertNotIn(self.appointment_b.id, appt_ids)

    def test_therapist_cannot_access_other_appointment(self):
        self.client.force_authenticate(user=self.therapist_a)
        response = self.client.get(f"/api/appointments/{self.appointment_b.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_therapist_cannot_create_appointment_for_other_patient(self):
        self.client.force_authenticate(user=self.therapist_a)
        future_slot = timezone.now() + timedelta(days=5)
        payload = {
            "patient": self.patient_b.id,
            "schedule_at": future_slot.isoformat(),
            "duration_minutes": 50,
            "price": "200.00",
        }
        response = self.client.post("/api/appointments/", payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_two_therapists_can_have_appointments_at_same_time(self):
        # Ambos os agendamentos foram criados em self.future_date para terapeutas diferentes
        self.assertEqual(self.appointment_a.schedule_at, self.appointment_b.schedule_at)
        # Terapeuta A agenda outro no mesmo horário dele -> deve rejeitar
        self.client.force_authenticate(user=self.therapist_a)
        payload = {
            "patient": self.patient_a.id,
            "schedule_at": self.future_date.isoformat(),
            "duration_minutes": 50,
            "price": "200.00",
        }
        response = self.client.post("/api/appointments/", payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    # ------------------ THERAPY SESSIONS ISOLATION ------------------

    def test_therapist_lists_only_own_sessions(self):
        self.client.force_authenticate(user=self.therapist_a)
        response = self.client.get("/api/therapy-sessions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get("results", response.data)
        session_ids = [s["id"] for s in results]
        self.assertIn(self.session_a.id, session_ids)
        self.assertNotIn(self.session_b.id, session_ids)

    def test_therapist_cannot_access_other_session(self):
        self.client.force_authenticate(user=self.therapist_a)
        response = self.client.get(f"/api/therapy-sessions/{self.session_b.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_therapist_cannot_create_session_for_other_patient(self):
        self.client.force_authenticate(user=self.therapist_a)
        payload = {
            "patient": self.patient_b.id,
            "session_date": timezone.now().isoformat(),
            "summary": "Tentativa indevida",
        }
        response = self.client.post("/api/therapy-sessions/", payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ------------------ PAYMENTS ISOLATION ------------------

    def test_therapist_lists_only_own_payments(self):
        self.client.force_authenticate(user=self.therapist_a)
        response = self.client.get("/api/payments/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get("results", response.data)
        payment_ids = [p["id"] for p in results]
        self.assertIn(self.payment_a.id, payment_ids)
        self.assertNotIn(self.payment_b.id, payment_ids)

    def test_therapist_cannot_access_other_payment(self):
        self.client.force_authenticate(user=self.therapist_a)
        response = self.client.get(f"/api/payments/{self.payment_b.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_therapist_cannot_create_payment_for_other_patient(self):
        self.client.force_authenticate(user=self.therapist_a)
        payload = {
            "patient": self.patient_b.id,
            "amount": "150.00",
            "status": "pending",
        }
        response = self.client.post("/api/payments/", payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ------------------ PASSWORD CHANGE ------------------

    def test_change_password_success(self):
        self.client.force_authenticate(user=self.therapist_a)
        payload = {
            "old_password": "password123",
            "new_password": "new_password456",
        }
        response = self.client.post("/api/change-password/", payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.therapist_a.refresh_from_db()
        self.assertTrue(self.therapist_a.check_password("new_password456"))

    def test_change_password_wrong_old_password_rejected(self):
        self.client.force_authenticate(user=self.therapist_a)
        payload = {
            "old_password": "senha_errada",
            "new_password": "new_password456",
        }
        response = self.client.post("/api/change-password/", payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_too_short_rejected(self):
        self.client.force_authenticate(user=self.therapist_a)
        payload = {
            "old_password": "password123",
            "new_password": "123",
        }
        response = self.client.post("/api/change-password/", payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
