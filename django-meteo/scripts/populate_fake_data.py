import os
import sys
import django
import random
from django.utils.timezone import now, timedelta
from datetime import datetime

from django.utils.timezone import make_aware

# Ensure the script runs from the Django project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meteo.settings")
django.setup()

from api.models import Station, WeatherData, MinMaxData, SystemStatus

# ✅ Define test stations with assigned IPs
stations_data = [
    {"station_ref": "esp32-001", "name": "Test Weather Station", "location": "Test Lab", "http_address": "http://127.0.0.1:5000"},
    {"station_ref": "esp32-002", "name": "Outdoor Station", "location": "Garden", "http_address": "http://127.0.0.1:5001"},
    {"station_ref": "esp32-003", "name": "Indoor Station", "location": "Living Room", "http_address": "http://127.0.0.1:5002"}
]

# ✅ Helper function to format timestamps as `YYYYMMDDHHMISS`
def format_timestamp(dt):
    return dt.strftime("%Y%m%d%H%M%S")

# ✅ Helper function to format dates as `YYYYMMDD`
def format_date(dt):
    return dt.strftime("%Y%m%d")

# ✅ Convert `YYYYMMDDHHMISS` string to Django `datetime` format

def parse_custom_datetime(ts):
    naive_dt = datetime.strptime(ts, "%Y%m%d%H%M%S")  # Converts to naive datetime
    return make_aware(naive_dt)  # Converts to timezone-aware datetime

def parse_custom_date(date_str):
    return datetime.strptime(date_str, "%Y%m%d").date()  # Converts to `YYYY-MM-DD`


for station_info in stations_data:
    station, created = Station.objects.get_or_create(
        station_ref=station_info["station_ref"],
        defaults={
            "name": station_info["name"],
            "location": station_info["location"],
            "http_address": station_info["http_address"]
        }
    )

    if created:
        print(f"✅ Added new station: {station_info['name']} ({station_info['station_ref']}) with IP {station_info['http_address']}")
    else:
        print(f"ℹ️ Station {station_info['name']} already exists.")

    # 📌 Generate 24 hours of weather data (one record every 30 minutes)
    for i in range(48):  # 24 hours * 2 (every 30 minutes)
        timestamp = now() - timedelta(minutes=i * 30)  # Decreasing timestamps every 30 mins
        WeatherData.objects.create(
            station=station,
            temperature=round(random.uniform(18.0, 35.0), 1),  # ✅ Rounded to 1 decimal
            humidity=round(random.uniform(30.0, 80.0), 1),  # ✅ Rounded to 1 decimal
            timestamp=parse_custom_datetime(format_timestamp(timestamp))  # ✅ Fix: Convert back to datetime
        )

    print(f"✅ 48 weather records (every 30 min) added for {station_info['name']}.")

    # 📌 Generate 7 days of Min/Max Data
    for i in range(7):
        date = now().date() - timedelta(days=i)
        MinMaxData.objects.update_or_create(
            station=station,
            date=parse_custom_date(format_date(date)),  # ✅ Use new format
            defaults={
                "min_temperature": round(random.uniform(15.0, 25.0), 1),
                "max_temperature": round(random.uniform(30.0, 40.0), 1),
                "min_humidity": round(random.uniform(30.0, 50.0), 1),
                "max_humidity": round(random.uniform(60.0, 80.0), 1)
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
