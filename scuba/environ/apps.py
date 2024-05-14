from django.apps import AppConfig


class EnvironConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'scuba.environ'

    def ready(self):
        import scuba.accounts.signals   # noqa: F401
