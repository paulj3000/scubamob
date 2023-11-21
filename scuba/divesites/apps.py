from django.apps import AppConfig


class DivesitesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'scuba.divesites'

    def ready(self):
        import scuba.divesites.signals
