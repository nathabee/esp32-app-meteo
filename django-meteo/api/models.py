from django.db import models 
  

from django.db import models

class Station(models.Model):
    """ Represents an ESP32 station with an internal ID, external reference, and HTTP address """
    station_ref = models.CharField(max_length=100, unique=True)  # External reference (e.g., "esp32-001")
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True, null=True)
    http_address = models.URLField(max_length=255, blank=True, null=True)  # Store ESP32 HTTP address
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.station_ref}) - {self.http_address}"


class WeatherData(models.Model):
    """ Stores temperature & humidity readings for each station, referencing internal ID """
    station = models.ForeignKey(Station, on_delete=models.CASCADE)  # Internal ID reference
    timestamp = models.DateTimeField()
    temperature = models.FloatField()
    humidity = models.FloatField()

    def __str__(self):
        return f"{self.timestamp} - {self.station.station_ref}: {self.temperature}°C, {self.humidity}%"


class SystemStatus(models.Model):
    """ Stores system status for ESP32 stations, referencing internal ID """
    station = models.ForeignKey(Station, on_delete=models.CASCADE)  # Internal ID reference
    timestamp = models.DateTimeField(auto_now_add=True)
    uptime_ms = models.BigIntegerField()
    free_heap = models.IntegerField()
    wifi_strength = models.IntegerField()

    def __str__(self):
        return f"{self.timestamp} - {self.station.station_ref} Status"


class MinMaxData(models.Model):
    """ Stores min/max temperature & humidity per day for each station, referencing internal ID """
    station = models.ForeignKey(Station, on_delete=models.CASCADE)  # Internal ID reference
    date = models.DateField()  # One entry per day per station
    min_temperature = models.FloatField()
    max_temperature = models.FloatField()
    min_humidity = models.FloatField()
    max_humidity = models.FloatField()

    def __str__(self):
        return f"{self.date} - {self.station.station_ref}: Min {self.min_temperature}°C, Max {self.max_temperature}°C"
