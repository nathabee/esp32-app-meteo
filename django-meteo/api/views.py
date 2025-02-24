from django.http import JsonResponse
from django.utils.timezone import now, timedelta
from django.db.models import Min, Max
from django.views.decorators.csrf import csrf_exempt
import json
#from django.utils.dateparse import parse_datetime
from .models import Station, WeatherData, MinMaxData, SystemStatus

from django.utils.timezone import localtime


from datetime import datetime

def parse_custom_datetime(ts):
    """ Convert 'YYYYMMDDHHMISS' to a valid datetime object. """
    try:
        return datetime.strptime(ts, "%Y%m%d%H%M%S")
    except ValueError:
        return None



def get_client_ip(request):
    """ Retrieve the IP address of the device making the request """
    ip = request.META.get('REMOTE_ADDR')

    # If behind a proxy/load balancer, use X-Forwarded-For
    forwarded_ip = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded_ip:
        ip = forwarded_ip.split(',')[0]  # Get the first IP in the list

    return ip  # Return only IP, no JSON response

 
# ✅ GET /api/stations/ - Get list of registered ESP32 stations
def list_stations(request):
    stations = Station.objects.all().values("station_ref", "name", "location", "created_at")

    response = {
        "stations": [
            {
                "id": s["station_ref"],
                "name": s["name"],
                "loc": s["location"],
                "created": localtime(s["created_at"]).strftime("%Y%m%d%H%M%S")  # ✅ Correct Date Format
            }
            for s in stations
        ]
    }

    return JsonResponse(response)


# ✅ **GET /api/status/<station_ref>/** - Get ESP32 system status
def status(request, station_ref):
    try:
        station = Station.objects.get(station_ref=station_ref)
        latest_status = SystemStatus.objects.filter(station=station).order_by('-timestamp').first()

        if latest_status:
            response = {
                "id": station_ref,
                "ts": latest_status.timestamp.strftime("%Y%m%d%H%M%S"),
                "upt": latest_status.uptime_ms,
                "mem": latest_status.free_heap,
                "wif": latest_status.wifi_strength
            }
        else:
            response = {"error": "No system status available"}

    except Station.DoesNotExist:
        response = {"error": "Station not found"}

    return JsonResponse(response)


# ✅ **GET /api/lastreport/<station_ref>/** - Get latest weather report 
def last_report(request, station_ref):
    try:
        station = Station.objects.get(station_ref=station_ref)
        latest_data = WeatherData.objects.filter(station=station).order_by('-timestamp').first()

        if latest_data:
            response = {
                "id": station_ref,
                "ts": latest_data.timestamp.strftime("%Y%m%d%H%M%S"),
                "tmp": round(latest_data.temperature, 1),  # ✅ Ensure 1 decimal precision
                "hum": round(latest_data.humidity, 1)  # ✅ Ensure 1 decimal precision
            }
        else:
            response = {"error": "No weather data available"}

    except Station.DoesNotExist:
        response = {"error": "Station not found"}

    return JsonResponse(response)



# ✅ **GET /api/history/<station_ref>/** - Get ESP32 weather history 
def history(request, station_ref):
    try:
        station = Station.objects.get(station_ref=station_ref)
        weather_data = WeatherData.objects.filter(station=station).order_by('-timestamp')[:50]

        response = {
            "id": station_ref,
            "history": [
                {
                    "ts": entry.timestamp.strftime("%Y%m%d%H%M%S"),
                    "tmp": round(entry.temperature, 1),  # ✅ Ensure 1 decimal precision
                    "hum": round(entry.humidity, 1)  # ✅ Ensure 1 decimal precision
                }
                for entry in weather_data
            ]
        }
    except Station.DoesNotExist:
        response = {"error": "Station not found"}

    return JsonResponse(response)



# ✅ **GET /api/minmax/history/<station_ref>/** - Get ESP32 min/max records 
def maxima_history(request, station_ref):
    try:
        station = Station.objects.get(station_ref=station_ref)
        response = {"id": station_ref, "history": []}

        for i in range(7):
            day = now() - timedelta(days=i)
            daily_data = WeatherData.objects.filter(station=station, timestamp__date=day.date())

            if daily_data.exists():
                min_temp = round(daily_data.aggregate(Min('temperature'))["temperature__min"], 1)
                max_temp = round(daily_data.aggregate(Max('temperature'))["temperature__max"], 1)
                min_hum = round(daily_data.aggregate(Min('humidity'))["humidity__min"], 1)
                max_hum = round(daily_data.aggregate(Max('humidity'))["humidity__max"], 1)

                response["history"].append({
                    "dt": day.strftime("%Y%m%d"),
                    "tmin": min_temp,
                    "tmax": max_temp,
                    "hmin": min_hum,
                    "hmax": max_hum
                })
    except Station.DoesNotExist:
        response = {"error": "Station not found"}

    return JsonResponse(response)


# ✅ **GET /api/lastupdate/<station_ref>/** - Get last update timestamp
def last_update(request, station_ref):
    try:
        station = Station.objects.get(station_ref=station_ref)
        client_ip = get_client_ip(request)

        # Check if IP matches the stored HTTP address
        if station.http_address and not station.http_address.startswith(f"http://{client_ip}"):
            return JsonResponse({"error": "IP and ID not coherent"}, status=403)

        # Get last recorded weather data timestamp
        last_entry = WeatherData.objects.filter(station=station).order_by('-timestamp').first()
        
        last_ts = last_entry.timestamp.strftime("%Y%m%d%H%M%S") if last_entry else "19700101 00:00"

        return JsonResponse({"id": station_ref, "ts": last_ts})

    except Station.DoesNotExist:
        return JsonResponse({"error": "Station not defined"}, status=404)

# ✅ **PUT /api/weather/upload/** - ESP32 uploads weather data
@csrf_exempt
def receive_weather_data(request):
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            station_ref = data.get("id")
            client_ip = get_client_ip(request)

            # ✅ Ensure station exists
            try:
                station = Station.objects.get(station_ref=station_ref)
            except Station.DoesNotExist:
                return JsonResponse({"error": "Station not defined"}, status=404)

            # ✅ Validate IP address (if `http_address` is set)
            if station.http_address and not station.http_address.startswith(f"http://{client_ip}"):
                return JsonResponse({"error": "IP and ID not coherent"}, status=403)

            # ✅ Check for "data" key
            if "data" not in data or not isinstance(data["data"], list):
                return JsonResponse({"error": "Invalid data format. Expected a list."}, status=400)

            # ✅ Process data
            weather_entries = []
            for record in data["data"]:
                timestamp = parse_custom_datetime(record["ts"])
                if not timestamp:
                    return JsonResponse({"error": f"Invalid timestamp format: {record['ts']}"}, status=400)

                weather_entries.append(
                    WeatherData(
                        station=station,
                        timestamp=timestamp,
                        temperature=round(record["tmp"], 1),
                        humidity=round(record["hum"], 1)
                    )
                )

            # ✅ Save data & return count
            saved_entries = WeatherData.objects.bulk_create(weather_entries)
            return JsonResponse({"msg": "Weather data received", "count": len(saved_entries)}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=400)


 
# ✅ **PUT /api/minmax/upload/** - Receive ESP32 min/max data with IP validation
@csrf_exempt
def receive_minmax_data(request):
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            station_ref = data.get("id")
            client_ip = get_client_ip(request)

            # ✅ Retrieve station and validate HTTP address
            try:
                station = Station.objects.get(station_ref=station_ref)
            except Station.DoesNotExist:
                return JsonResponse({"error": "Station not found"}, status=404)

            # ✅ Ensure request comes from the correct IP
            if station.http_address:
                expected_ip = station.http_address.replace("http://", "").split(":")[0]
                if client_ip != expected_ip:
                    return JsonResponse({"error": "IP and ID not coherent"}, status=403)


            minmax_entries = []
            for record in data.get("data", []):
                dt = record["dt"]  # "YYYYMMDD" format
                try:
                    date_obj = now().strptime(dt, "%Y%m%d").date()
                except ValueError:
                    return JsonResponse({"error": f"Invalid date format: {dt}"}, status=400)

                minmax_entries.append(
                    MinMaxData(
                        station=station,
                        date=date_obj,
                        min_temperature=round(record["tmin"], 1),
                        max_temperature=round(record["tmax"], 1),
                        min_humidity=round(record["hmin"], 1),
                        max_humidity=round(record["hmax"], 1)
                    )
                )

            MinMaxData.objects.bulk_create(minmax_entries)

            return JsonResponse({"msg": "Min/Max data received", "count": len(minmax_entries)}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


# ✅ **PUT /api/status/upload/** - Handle ESP32 system status update with IP validation
@csrf_exempt
def receive_status_data(request):
    if request.method == "PUT":
        try:
            data = json.loads(request.body.decode("utf-8"))
            station_ref = data.get("id")
            uptime = data.get("upt")
            free_heap = data.get("mem")
            wifi_strength = data.get("wif")
            timestamp = data.get("ts")  # Add timestamp field
            client_ip = get_client_ip(request)

            try:
                station = Station.objects.get(station_ref=station_ref)
            except Station.DoesNotExist:
                return JsonResponse({"error": "Station not defined"}, status=404)

            if station.http_address and not station.http_address.startswith(f"http://{client_ip}"):
                return JsonResponse({"error": "IP and ID not coherent"}, status=403)

            # Convert timestamp format
            ts_parsed = parse_custom_datetime(timestamp)
            if not ts_parsed:
                return JsonResponse({"error": f"Invalid timestamp format: {timestamp}"}, status=400)

            SystemStatus.objects.create(
                station=station,
                timestamp=ts_parsed,  # Store the timestamp
                uptime_ms=uptime,
                free_heap=free_heap,
                wifi_strength=wifi_strength
            )

            return JsonResponse({"msg": "System status updated"}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
