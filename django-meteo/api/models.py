from django.db import models
from django.utils.timezone import now, timedelta
from django.db.models import Min, Max

class Station(models.Model):
    """ Represents an ESP32 station """
    station_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.station_id})"


class WeatherData(models.Model):
    """ Stores temperature & humidity readings for each station """
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    temperature = models.FloatField()
    humidity = models.FloatField()

    def __str__(self):
        return f"{self.timestamp} - {self.station.name}: {self.temperature}°C, {self.humidity}%"


class SystemStatus(models.Model):
    """ Stores system status for ESP32 stations """
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    uptime_ms = models.BigIntegerField()
    free_heap = models.IntegerField()
    wifi_strength = models.IntegerField()

    def __str__(self):
        return f"{self.timestamp} - {self.station.name} Status"


class MinMaxData(models.Model):
    """ Stores min/max temperature & humidity per day for each station """
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    date = models.DateField()  # One entry per day per station
    min_temperature = models.FloatField()
    max_temperature = models.FloatField()
    min_humidity = models.FloatField()
    max_humidity = models.FloatField()

    def __str__(self):
        return f"{self.date} - {self.station.name}: Min {self.min_temperature}°C, Max {self.max_temperature}°C"
