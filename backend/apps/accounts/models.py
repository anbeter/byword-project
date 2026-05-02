from django.db import models
from django.contrib.auth.models import User

from apps.core.models_base import TimeStampedModel, DateRangeModel


class StudentProfile(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    enrollment_number = models.CharField(max_length=50, unique=True)

    birth_date = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)

    is_active = models.BooleanField(default=True)
    enrollment_date = models.DateField(auto_now_add=True)

    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.enrollment_number} - {self.user.get_full_name()}"


class StudentStatusHistory(TimeStampedModel, DateRangeModel):
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="status_history"
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ("active", "Active"),
            ("inactive", "Inactive"),
            ("blocked", "Blocked"),
        ],
        default="active"
    )

    reason = models.TextField(blank=True)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.student} - {self.status}"