from django.core.management.base import BaseCommand
from apps.academic.models import BlockedSchedule
from apps.core.choices import DayOfWeek


class Command(BaseCommand):
    help = "Create lunch time blocks (12:00 - 14:00)"

    def handle(self, *args, **kwargs):
        for day in DayOfWeek.weekdays():
            BlockedSchedule.objects.get_or_create(
                day_of_week=day,
                start_time="12:00",
                duration_minutes=120,
                defaults={
                    "reason": "Lunch time",
                    "is_active": True,
                }
            )

        self.stdout.write(self.style.SUCCESS("Lunch blocks created."))
