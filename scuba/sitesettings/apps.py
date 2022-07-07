from django.apps import AppConfig


class SiteSettingsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'scuba.sitesettings'

    def ready(self):
        import scuba.sitesettings.signals
