# Register your models here.
from django.contrib import admin
from .models import Station, WeatherData, SystemStatus,MinMaxData

admin.site.register(Station)
admin.site.register(WeatherData)
admin.site.register(SystemStatus)
admin.site.register(MinMaxData)