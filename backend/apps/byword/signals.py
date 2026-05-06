from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Lesson
from apps.byword.services.services_activity import create_default_activity


@receiver(post_save, sender=Lesson)
def create_activity(sender, instance, created, **kwargs):
    if created:
        create_default_activity(instance)