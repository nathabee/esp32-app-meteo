from django.http import JsonResponse
from django.utils.timezone import now, timedelta
from django.db.models import Min, Max
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils.dateparse import parse_datetime
from .models import Station, WeatherData, MinMaxData, SystemStatus


# ✅ **GET /api/stations/** - Get list of registered ESP32 stations
def list_stations(request):
    stations = Station.objects.all().values("station_id", "name", "location", "created_at")
    
    response = {
        "stations": [
            {"id": s["station_id"], "name": s["name"], "loc": s["location"], "created": s["created_at"]}
            for s in stations
        ]
    }

    return JsonResponse(response)


# ✅ **GET /api/status/<station_id>/** - Get ESP32 system status
def status(request, station_id):
    try:
        station = Station.objects.get(station_id=station_id)
        latest_status = SystemStatus.objects.filter(station=station).order_by('-timestamp').first()

        if latest_status:
            response = {
                "id": station_id,
                "upt": latest_status.uptime_ms,
                "mem": latest_status.free_heap,
                "wif": latest_status.wifi_strength
            }
        else:
            response = {"error": "No system status available"}

    except Station.DoesNotExist:
        response = {"error": "Station not found"}

    return JsonResponse(response)


# ✅ **GET /api/lastreport/<station_id>/** - Get latest weather report
def last_report(request, station_id):
    try:
        station = Station.objects.get(station_id=station_id)
        latest_data = WeatherData.objects.filter(station=station).order_by('-timestamp').first()

        if latest_data:
            response = {
                "id": station_id,
                "ts": latest_data.timestamp.isoformat(),
                "tmp": latest_data.temperature,
                "hum": latest_data.humidity
            }
        else:
            response = {"error": "No weather data available"}

    except Station.DoesNotExist:
        response = {"error": "Station not found"}

    return JsonResponse(response)


# ✅ **GET /api/history/<station_id>/** - Get ESP32 weather history
def history(request, station_id):
    try:
        station = Station.objects.get(station_id=station_id)
        weather_data = WeatherData.objects.filter(station=station).order_by('-timestamp')[:50]

        response = {
            "id": station_id,
            "history": [
                {"ts": str(entry.timestamp), "tmp": entry.temperature, "hum": entry.humidity}
                for entry in weather_data
            ]
        }
    except Station.DoesNotExist:
        response = {"error": "Station not found"}

    return JsonResponse(response)


# ✅ **GET /api/minmax/history/<station_id>/** - Get ESP32 min/max records
def maxima_history(request, station_id):
    try:
        station = Station.objects.get(station_id=station_id)
        response = {"id": station_id, "history": []}

        for i in range(7):
            day = now() - timedelta(days=i)
            daily_data = WeatherData.objects.filter(station=station, timestamp__date=day.date())

            if daily_data.exists():
                min_temp = daily_data.aggregate(Min('temperature'))["temperature__min"]
                max_temp = daily_data.aggregate(Max('temperature'))["temperature__max"]
                min_hum = daily_data.aggregate(Min('humidity'))["humidity__min"]
                max_hum = daily_data.aggregate(Max('humidity'))["humidity__max"]

                response["history"].append({
                    "dt": str(day.date()),
                    "tmin": min_temp,
                    "tmax": max_temp,
                    "hmin": min_hum,
                    "hmax": max_hum
                })
    except Station.DoesNotExist:
        response = {"error": "Station not found"}

    return JsonResponse(response)


# ✅ **GET /api/lastupdate/<station_id>/** - Get last update timestamp
def last_update(request, station_id):
    try:
        station = Station.objects.get(station_id=station_id)
        last_entry = WeatherData.objects.filter(station=station).order_by('-timestamp').first()
        response = {"ts": last_entry.timestamp.isoformat() if last_entry else None}

    except Station.DoesNotExist:
        response = {"error": "Station not found"}

    return JsonResponse(response)


# ✅ **PUT /api/weather/upload/** - Receive ESP32 batch weather data
@csrf_exempt
def receive_weather_data(request):
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            station_id = data.get("id")

            station = Station.objects.get(station_id=station_id)

            weather_entries = []
            for record in data.get("data", []):
                weather_entries.append(
                    WeatherData(
                        station=station,
                        timestamp=parse_datetime(record["ts"]),
                        temperature=record["tmp"],
                        humidity=record["hum"]
                    )
                )

            WeatherData.objects.bulk_create(weather_entries)

            return JsonResponse({"msg": "Weather data received", "count": len(weather_entries)}, status=201)

        except Station.DoesNotExist:
            return JsonResponse({"error": "Station not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=400)


# ✅ **PUT /api/minmax/upload/** - Receive ESP32 min/max data
@csrf_exempt
def receive_minmax_data(request):
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            station_id = data.get("id")

            station = Station.objects.get(station_id=station_id)

            minmax_entries = []
            for record in data.get("data", []):
                minmax_entries.append(
                    MinMaxData(
                        station=station,
                        date=parse_datetime(record["dt"]).date(),
                        min_temperature=record["tmin"],
                        max_temperature=record["tmax"],
                        min_humidity=record["hmin"],
                        max_humidity=record["hmax"]
                    )
                )

            MinMaxData.objects.bulk_create(minmax_entries)

            return JsonResponse({"msg": "Min/Max data received", "count": len(minmax_entries)}, status=201)

        except Station.DoesNotExist:
            return JsonResponse({"error": "Station not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=400)


# ✅ **PUT /api/status/upload/** - Handle ESP32 system status update
@csrf_exempt 
def receive_status_data(request):
    if request.method == "PUT":
        try:
            data = json.loads(request.body.decode("utf-8"))
            station_id = data.get("id")
            uptime = data.get("upt")
            free_heap = data.get("mem")
            wifi_strength = data.get("wif")

            station = Station.objects.get(station_id=station_id)

            SystemStatus.objects.create(
                station=station,
                uptime_ms=uptime,
                free_heap=free_heap,
                wifi_strength=wifi_strength
            )

            return JsonResponse({"msg": "System status updated"}, status=200)
        except Station.DoesNotExist:
            return JsonResponse({"error": "Station not found"}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)
