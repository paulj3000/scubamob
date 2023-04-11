from django.contrib import admin

from scuba.weather.models import Weather, WeatherPostalCode


class WeatherAdmin(admin.ModelAdmin):
    list_display = ('name', 'region', 'country', 'lat', 'lng',)


admin.site.register(Weather, WeatherAdmin)
admin.site.register(WeatherPostalCode)
