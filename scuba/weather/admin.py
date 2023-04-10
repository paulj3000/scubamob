from django.contrib import admin

from scuba.weather.models import Weather


class WeatherAdmin(admin.ModelAdmin):
    list_display = ('name', 'region', 'country', 'lat', 'long',)

admin.site.register(Weather, WeatherAdmin)
