from flask import Flask, jsonify
import requests  # To communicate with Django server

app = Flask(__name__)

# ✅ Constants
STATION_ID = "esp32-001"
DJANGO_API_BASE = "http://127.0.0.1:8000/api"

# ✅ Simulated 24-Hour Weather Data (One Record Every 30 Minutes)
weather_data = {
    "esp32-001": [
        {"ts": f"2025-02-20 {hour:02}:{minute:02}:00", "tmp": 18.0 + (hour / 2.0), "hum": 40.0 + (hour / 4.0)}
        for hour in range(0, 24) for minute in [0, 30]
    ]
}

# ✅ Simulated 7-Day Min/Max Data
minmax_data = {
    "esp32-001": [
        {"dt": "2025-02-19", "tmin": 14.3, "tmax": 29.1, "hmin": 38.1, "hmax": 55.0},
        {"dt": "2025-02-18", "tmin": 13.8, "tmax": 28.4, "hmin": 37.6, "hmax": 54.3},
        {"dt": "2025-02-17", "tmin": 14.1, "tmax": 27.9, "hmin": 36.9, "hmax": 52.8}
    ]
}

# ✅ Simulated System Status
system_status = {"esp32-001": {"upt": 150000, "mem": 220000, "wif": -70}}

 

# ✅ **GET /api/status/esp32-001/** - Get ESP32 system status
@app.route('/api/status/<station_id>/', methods=['GET'])
def status(station_id):
    if station_id in system_status:
        return jsonify({"id": station_id, **system_status[station_id]})
    return jsonify({"error": "Station not found"}), 404

# ✅ **GET /api/lastreport/esp32-001/** - Get latest weather report
@app.route('/api/lastreport/<station_id>/', methods=['GET'])
def last_report(station_id):
    if station_id in weather_data and weather_data[station_id]:
        return jsonify({"id": station_id, **weather_data[station_id][-1]})
    return jsonify({"error": "No weather data available"}), 404

# ✅ **GET /api/history/esp32-001/** - Get ESP32 weather history
@app.route('/api/history/<station_id>/', methods=['GET'])
def history(station_id):
    if station_id in weather_data:
        return jsonify({"id": station_id, "history": weather_data[station_id]})
    return jsonify({"error": "No history found"}), 404

# ✅ **GET /api/minmax/history/esp32-001/** - Get ESP32 min/max records
@app.route('/api/minmax/history/<station_id>/', methods=['GET'])
def maxima_history(station_id):
    if station_id in minmax_data:
        return jsonify({"id": station_id, "history": minmax_data[station_id]})
    return jsonify({"error": "No min/max data available"}), 404

# ✅ **GET /api/lastupdate/esp32-001/** - Get last update timestamp
@app.route('/api/lastupdate/<station_id>/', methods=['GET'])
def last_update(station_id):
    if station_id in weather_data and weather_data[station_id]:
        return jsonify({"ts": weather_data[station_id][-1]["ts"]})
    return jsonify({"error": "No weather data found"}), 404




# ✅ Simulated System Status
system_status = {"esp32-001": {"upt": 150000, "mem": 220000, "wif": -70}}

# ✅ **GET /api/sync/** - ESP32 sync process simulation (default station)
@app.route('/api/sync/', methods=['GET'])
def trigger_sync_default():
    """ Calls trigger_sync with the default station ID. """
    return trigger_sync(STATION_ID)

# ✅ **GET /api/sync/<station_id>/** - ESP32 sync process simulation (specific station)
@app.route('/api/sync/<station_id>/', methods=['GET'])
def trigger_sync(station_id=STATION_ID):
    """ Syncs weather, min/max, and system status data to Django. """
    print(f"🔄 Sync triggered for station {station_id}")

    last_update = get_last_update(station_id)
    if not last_update:
        return jsonify({"error": "Failed to fetch last update timestamp"}), 500

    # Fetch new weather and min/max data
    fetched_weather_data = fetch_data_from_django("history", station_id)
    fetched_minmax_data = fetch_data_from_django("minmax/history", station_id)

    # Upload weather data
    if fetched_weather_data:
        upload_to_django("weather/upload/", {"id": station_id, "data": fetched_weather_data})

    # Upload min/max data
    if fetched_minmax_data:
        upload_to_django("minmax/upload/", {"id": station_id, "data": fetched_minmax_data})

    # Upload system status
    if station_id in system_status:
        upload_to_django("status/upload/", {"id": station_id, **system_status[station_id]})

    if fetched_weather_data or fetched_minmax_data:
        return jsonify({"msg": f"Sync completed for {station_id}"})
    else:
        return jsonify({"error": "No new data to sync"}), 204

# ✅ **Helper: Fetch Data from Django API**
def fetch_data_from_django(endpoint, station_id):
    """ Fetches historical or min/max data from Django API. """
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
    """ Sends updated data to Django API via PUT request. """
    try:
        url = f"{DJANGO_API_BASE}/{endpoint}"
        response = requests.put(url, json=payload)
        print(f"📡 {endpoint} upload response: HTTP {response.status_code} {response.text}")
    except Exception as e:
        print(f"❌ Error uploading {endpoint}: {e}")

# ✅ **Helper: Get Last Update Timestamp from Django**
def get_last_update(station_id):
    """ Retrieves the last update timestamp for the given station. """
    try:
        url = f"{DJANGO_API_BASE}/lastupdate/{station_id}/"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get("ts", "1970-01-01 00:00:00")
        print(f"❌ Failed to fetch last update timestamp for {station_id}! HTTP {response.status_code}")
        return None
    except Exception as e:
        print(f"❌ Error fetching last update: {e}")
        return None

# ✅ Run Flask ESP32 Mock Server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)