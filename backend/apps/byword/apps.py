from django.apps import AppConfig


class BywordConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.byword'

    def ready(self):
        import apps.byword.signals