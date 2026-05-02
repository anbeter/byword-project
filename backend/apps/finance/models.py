from django.db import models

from apps.core.models_base import TimeStampedModel, DateRangeModel
from apps.accounts.models import StudentProfile
from apps.academic.models import Class


class FinancialStatus(TimeStampedModel, DateRangeModel):
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="financial_statuses"
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ("paid", "Paid"),
            ("pending", "Pending"),
            ("overdue", "Overdue"),
            ("scholarship", "Scholarship"),
        ]
    )

    reference_month = models.DateField()

    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-reference_month"]
        unique_together = ("student", "reference_month")

    def __str__(self):
        return f"{self.student} - {self.reference_month} - {self.status}"


class Payment(TimeStampedModel):
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="payments"
    )

    class_obj = models.ForeignKey(
        Class,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="payments"
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    payment_date = models.DateField()
    reference_month = models.DateField()

    payment_method = models.CharField(
        max_length=20,
        choices=[
            ("cash", "Cash"),
            ("credit_card", "Credit Card"),
            ("debit_card", "Debit Card"),
            ("pix", "PIX"),
            ("bank_transfer", "Bank Transfer"),
        ]
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ("confirmed", "Confirmed"),
            ("pending", "Pending"),
            ("failed", "Failed"),
        ],
        default="confirmed"
    )

    transaction_id = models.CharField(max_length=100, blank=True)

    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.student} - {self.amount}"