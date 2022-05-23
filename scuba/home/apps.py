from django.apps import AppConfig


class HomeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'scuba.home'

    def ready(self):
        import scuba.home.signals
