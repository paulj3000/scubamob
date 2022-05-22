from django.apps import AppConfig


class GalleryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'scuba.gallery'

    def ready(self):
        import scuba.gallery.signals
