from django.db import models
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError

from apps.core.models_base import TimeStampedModel, DateRangeModel
from apps.core.choices import DayOfWeek
from apps.accounts.models import StudentProfile

# from .models import BlockedSchedule


class BlockedSchedule(TimeStampedModel):
    day_of_week = models.IntegerField(
        choices=DayOfWeek.choices
    )

    start_time = models.TimeField()
    duration_minutes = models.PositiveIntegerField()

    reason = models.CharField(max_length=255, blank=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"BLOCKED - {self.get_day_of_week_display()} {self.start_time}"

    def get_start_end(self):
        from datetime import datetime, timedelta
        start = datetime.combine(datetime.today(), self.start_time)
        end = start + timedelta(minutes=self.duration_minutes)
        return start, end



class Class(TimeStampedModel):
    name = models.CharField(max_length=100)

    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    description = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


# 💰 Histórico de preço da turma
class ClassPrice(TimeStampedModel, DateRangeModel):
    class_obj = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name="prices"
    )

    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.class_obj} - {self.price}"


# 🎓 Matrícula do aluno na turma
class Enrollment(TimeStampedModel, DateRangeModel):
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="enrollments"
    )

    class_obj = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name="enrollments"
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ("active", "Active"),
            ("inactive", "Inactive"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        default="active"
    )

    class Meta:
        unique_together = ("student", "class_obj", "start_date")

    def __str__(self):
        return f"{self.student} → {self.class_obj}"


# 🕒 Horários da turma (múltiplos)
class ClassSchedule(TimeStampedModel):
    class_obj = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name="schedules"
    )

    day_of_week = models.IntegerField(
        choices=DayOfWeek.business_choices2()
    )

    start_time = models.TimeField()
    duration_minutes = models.PositiveIntegerField()

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["day_of_week", "start_time"]

    def __str__(self):
        return f"{self.class_obj} - {self.get_day_of_week_display()} {self.start_time}"


    # ⏱️ cálculo do horário final
    @property
    def end_time(self):
        if not self.start_time or not self.duration_minutes:
            return None

        dt = datetime.combine(datetime.today(), self.start_time)
        dt_end = dt + timedelta(minutes=self.duration_minutes)
        return dt_end.time()


    def get_start_end(self):
        start = datetime.combine(datetime.today(), self.start_time)
        end = start + timedelta(minutes=self.duration_minutes)
        return start, end


    def clean(self):
        qs = ClassSchedule.objects.filter(
            class_obj=self.class_obj,
            day_of_week=self.day_of_week,
            is_active=True
        )

        if self.pk:
            qs = qs.exclude(pk=self.pk)

        current_start, current_end = self.get_start_end()

        for obj in qs:
            obj_start, obj_end = obj.get_start_end()

            if current_start < obj_end and obj_start < current_end:
                raise ValidationError(
                    f"Schedule conflict with {obj.start_time} - {obj.end_time}"
                )


    def clean(self):
        from django.core.exceptions import ValidationError

        current_start, current_end = self.get_start_end()

        # 🔹 conflito com outras turmas
        qs = ClassSchedule.objects.filter(
            class_obj=self.class_obj,
            day_of_week=self.day_of_week,
            is_active=True
        )

        if self.pk:
            qs = qs.exclude(pk=self.pk)

        for obj in qs:
            obj_start, obj_end = obj.get_start_end()

            if current_start < obj_end and obj_start < current_end:
                raise ValidationError("Conflict with another class schedule.")

        # 🔹 conflito com bloqueios
        blocked_qs = BlockedSchedule.objects.filter(
            day_of_week=self.day_of_week,
            is_active=True
        )

        for block in blocked_qs:
            block_start, block_end = block.get_start_end()

            if current_start < block_end and block_start < current_end:
                raise ValidationError(
                    f"Conflict with blocked time: {block.start_time}"
                )
