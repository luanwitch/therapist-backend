from django.db import models
from patients.models import Patient
from appointments.models import Appointment

# Create your models here.
class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ("pix", "PIX"),
        ("money", "Dinheiro"),
        ("card", "Cartão"),
        ("transfer", "Transferência"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pendente"),
        ("paid", "Pago"),
        ("cancelled", "Cancelado"),
    ]

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="payments"
    )

    #Relacionamento de um para um entre pagamento e agendamento
    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="payment"
    ) 

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    paid_at = models.DateTimeField(blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)

    notes = models.TextField(blank=True, null= True)

    def __str__(self):
        return f"{self.patient.full_name} - R$ {self.amount} - {self.status} "