import os
import sys
import django
import random
from django.utils import timezone
from datetime import timedelta

# Ensure the script runs from the Django project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meteo.settings")
django.setup()

from api.models import Station, WeatherData, MinMaxData, SystemStatus

# 📌 Define test stations
stations_data = [
    {"station_id": "esp32-test-001", "name": "Test Weather Station", "location": "Test Lab"},
    {"station_id": "esp32-outdoor", "name": "Outdoor Station", "location": "Garden"},
    {"station_id": "esp32-indoor", "name": "Indoor Station", "location": "Living Room"}
]

for station_info in stations_data:
    station, created = Station.objects.get_or_create(
        station_id=station_info["station_id"],
        defaults={"name": station_info["name"], "location": station_info["location"]}
    )

    if created:
        print(f"✅ Added new station: {station_info['name']} ({station_info['station_id']})")
    else:
        print(f"ℹ️ Station {station_info['name']} already exists.")

    # 📌 Generate 24 hours of weather data (one record every hour)
    for i in range(24):
        timestamp = timezone.now() - timedelta(hours=i)
        WeatherData.objects.create(
            station=station,
            temperature=random.uniform(18.0, 35.0),  # Random temp
            humidity=random.uniform(30.0, 80.0),  # Random humidity
            timestamp=timestamp
        )

    print(f"✅ 24 weather records added for {station_info['name']}.")

    # 📌 Generate 7 days of Min/Max Data
    for i in range(7):
        date = timezone.now().date() - timedelta(days=i)
        MinMaxData.objects.update_or_create(
            station=station,
            date=date,
            defaults={
                "min_temperature": random.uniform(15.0, 25.0),
                "max_temperature": random.uniform(30.0, 40.0),
                "min_humidity": random.uniform(30.0, 50.0),
                "max_humidity": random.uniform(60.0, 80.0)
            }
        )

    print(f"✅ 7 days of min/max data added for {station_info['name']}.")

    # 📌 Generate latest system status
    SystemStatus.objects.update_or_create(
        station=station,
        defaults={
            "uptime_ms": random.randint(100000, 500000),
            "free_heap": random.randint(200000, 300000),
            "wifi_strength": random.randint(-80, -40)
        }
    )

    print(f"✅ System status added for {station_info['name']}.")

print("🎉 **Initial test data setup complete!**")
