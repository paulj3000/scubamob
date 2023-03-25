from django.apps import AppConfig


class ContentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'scuba.content'

    def ready(self):
        import scuba.content.signals
