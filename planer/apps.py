from django.apps import AppConfig


class PlanerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'planer'

    def ready(self):
        import planer.signals
