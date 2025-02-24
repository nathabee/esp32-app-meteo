from flask import Flask, jsonify, request
import requests
import sys

from datetime import datetime, timedelta

app = Flask(__name__)

# ✅ Mapping of ESP32 Station Numbers to IDs and Ports
STATIONS = {
    "1": {"station_id": "esp32-001", "port": 5000},
    "2": {"station_id": "esp32-002", "port": 5001},
    "3": {"station_id": "esp32-003", "port": 5002}
}

DJANGO_API_BASE = "http://127.0.0.1:8000/api"

# ✅ Accept station number as a parameter (default: "1")
station_number = sys.argv[1] if len(sys.argv) > 1 else "1"

if station_number not in STATIONS:
    print(f"❌ Invalid station number '{station_number}'. Please use 1, 2, or 3.")
    sys.exit(1)

# ✅ Set station-specific variables
STATION_ID = STATIONS[station_number]["station_id"]
PORT = STATIONS[station_number]["port"]

print(f"🚀 Starting ESP32 Mock Server: {STATION_ID} on port {PORT}")

# ✅ Helper function to format timestamp in YYYYMMDDHHMISS format
def format_timestamp(hour, minute=0):
    return datetime(2025, 2, 20, hour, minute).strftime("%Y%m%d%H%M%S")

# ✅ Simulated 24-Hour Weather Data (One Record Every 30 Minutes)
weather_data = {
    STATION_ID: [
        {"ts": format_timestamp(hour, minute), "tmp": round(18.0 + (hour / 2.0), 1), "hum": round(40.0 + (hour / 4.0), 1)}
        for hour in range(0, 24) for minute in [0, 30]
    ]
}

# ✅ Simulated 7-Day Min/Max Data
def format_date(day_offset):
    return (datetime(2025, 2, 20) - timedelta(days=day_offset)).strftime("%Y%m%d")

minmax_data = {
    STATION_ID: [
        {"dt": format_date(i), "tmin": round(14.0 + i * 0.2, 1), "tmax": round(28.0 + i * 0.3, 1), 
         "hmin": round(37.0 + i * 0.4, 1), "hmax": round(53.0 + i * 0.5, 1)}
        for i in range(7)
    ]
}

# ✅ Simulated System Status
system_status = {STATION_ID: {"upt": 150000, "mem": 220000, "wif": -70}}

# ✅ **API Routes**
@app.route('/api/status/<station_id>/', methods=['GET'])
def status(station_id):
    if station_id in system_status:
        return jsonify({"id": station_id, **system_status[station_id]})
    return jsonify({"error": "Station not found"}), 404

@app.route('/api/lastreport/<station_id>/', methods=['GET'])
def last_report(station_id):
    if station_id in weather_data and weather_data[station_id]:
        return jsonify({"id": station_id, **weather_data[station_id][-1]})
    return jsonify({"error": "No weather data available"}), 404

@app.route('/api/history/<station_id>/', methods=['GET'])
def history(station_id):
    if station_id in weather_data:
        return jsonify({"id": station_id, "history": weather_data[station_id]})
    return jsonify({"error": "No history found"}), 404

@app.route('/api/minmax/history/<station_id>/', methods=['GET'])
def maxima_history(station_id):
    if station_id in minmax_data:
        return jsonify({"id": station_id, "history": minmax_data[station_id]})
    return jsonify({"error": "No min/max data available"}), 404

@app.route('/api/lastupdate/<station_id>/', methods=['GET'])
def last_update(station_id):
    if station_id in weather_data and weather_data[station_id]:
        return jsonify({"ts": weather_data[station_id][-1]["ts"]})
    return jsonify({"error": "No weather data found"}), 404

@app.route('/api/sync/<station_id>/', methods=['GET'])
def trigger_sync(station_id=STATION_ID):
    print(f"🔄 Sync triggered for station {station_id}")
    last_update = get_last_update(station_id)
    if not last_update:
        return jsonify({"error": "Failed to fetch last update timestamp"}), 500

    fetched_weather_data = fetch_data_from_django("history", station_id)
    fetched_minmax_data = fetch_data_from_django("minmax/history", station_id)

    if fetched_weather_data:
        upload_to_django("weather/upload/", {"id": station_id, "data": fetched_weather_data})

    if fetched_minmax_data:
        upload_to_django("minmax/upload/", {"id": station_id, "data": fetched_minmax_data})

    if station_id in system_status:
        upload_to_django("status/upload/", {"id": station_id, **system_status[station_id]})

    if fetched_weather_data or fetched_minmax_data:
        return jsonify({"msg": f"Sync completed for {station_id}"})
    else:
        return jsonify({"error": "No new data to sync"}), 204

# ✅ **Helper: Fetch Data from Django API**
def fetch_data_from_django(endpoint, station_id):
    try:
        url = f"{DJANGO_API_BASE}/{endpoint}/{station_id}/"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get("history", [])
        print(f"❌ Failed to fetch {endpoint} for {station_id}! HTTP {response.status_code}")
        return []
    except Exception as e:
        print(f"❌ Error fetching {endpoint}: {e}")
        return []

# ✅ **Helper: Upload Data to Django API**
def upload_to_django(endpoint, payload):
    try:
        url = f"{DJANGO_API_BASE}/{endpoint}"
        response = requests.put(url, json=payload)
        print(f"📡 {endpoint} upload response: HTTP {response.status_code} {response.text}")
    except Exception as e:
        print(f"❌ Error uploading {endpoint}: {e}")

# ✅ **Helper: Get Last Update Timestamp from Django**
def get_last_update(station_id):
    try:
        url = f"{DJANGO_API_BASE}/lastupdate/{station_id}/"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get("ts", "19700101000000")
        print(f"❌ Failed to fetch last update timestamp for {station_id}! HTTP {response.status_code}")
        return None
    except Exception as e:
        print(f"❌ Error fetching last update: {e}")
        return None

# ✅ Run Flask ESP32 Mock Server
if __name__ == '__main__':
    print(f"🚀 Starting {STATION_ID} on port {PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=True)
