from django.apps import AppConfig


class GalleriesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'scuba.galleries'

    def ready(self):
        import scuba.galleries.signals
