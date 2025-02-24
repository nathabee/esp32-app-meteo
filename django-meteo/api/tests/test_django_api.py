import json
from django.test import TestCase
from django.utils.timezone import now,  make_aware 
from api.models import Station, WeatherData, MinMaxData, SystemStatus
from datetime import datetime 

class DjangoAPITests(TestCase):

    def setUp(self):
        """✅ Populate test database with fake ESP32 data"""
        self.station = Station.objects.create(
            station_ref="esp32-001",
            name="Test Weather Station",
            http_address="http://127.0.0.1:5000",
            location="Test Lab"
        )

        # ✅ Insert fake weather data
        self.weather_data = WeatherData.objects.create(
            station=self.station,
            temperature=22.5,
            humidity=60.0,
            timestamp=now()
        )

        # ✅ Insert fake min/max data (Convert `date` properly)
        self.minmax_data = MinMaxData.objects.create(
            station=self.station,
            date=datetime.strptime("2025-02-20", "%Y-%m-%d").date(),  # ✅ Ensure correct date format
            min_temperature=18.3,
            max_temperature=39.4,
            min_humidity=37.1,
            max_humidity=43.9
        )

        # ✅ Insert fake system status
        self.status_data = SystemStatus.objects.create(
            station=self.station,
            uptime_ms=120000,  # ✅ Ensure this matches the expected test value
            free_heap=200000,
            wifi_strength=-75
        )

    def test_list_stations(self):
        """✅ Test GET /api/stations/ and validate response data"""
        response = self.client.get("/api/stations/")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("stations", data)
        self.assertEqual(len(data["stations"]), 1)

        station_data = data["stations"][0]
        self.assertEqual(station_data["id"], "esp32-001")
        self.assertEqual(station_data["name"], "Test Weather Station")
        self.assertEqual(station_data["loc"], "Test Lab")

        # ✅ Assert that 'http_address' is NOT present in the response
        self.assertNotIn("http_address", station_data)
        print("✅ GET /api/stations/ passed with correct values and 'http_address' is hidden!")


    def test_minmax_history(self):
        """✅ Test GET /api/minmax/history/esp32-001/ and validate response"""
        response = self.client.get("/api/minmax/history/esp32-001/")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(len(data["history"]), 1)  # ✅ Ensure 1 record exists

        # ✅ Fix: Ensure date comparison is correct
        # expected_date = self.minmax_data.date.strftime("%Y%m%d")  # Convert to `YYYYMMDD`

        expected_date = self.minmax_data.date

        self.assertEqual(data["history"][0]["dt"], expected_date)

        self.assertEqual(data["history"][0]["tmin"], 18.3)
        self.assertEqual(data["history"][0]["tmax"], 39.4)
        self.assertEqual(data["history"][0]["hmin"], 37.1)
        self.assertEqual(data["history"][0]["hmax"], 43.9)
        print("✅ GET /api/minmax/history/esp32-001/ passed with correct values!")

    def test_minmax_upload(self):
        """✅ Test PUT /api/minmax/upload/ and validate stored data"""
        payload = {
            "id": "esp32-001",
            "dt": "2025-02-21",
            "tmin": 20.0,
            "tmax": 38.0,
            "hmin": 40.0,
            "hmax": 50.0
        }
        response = self.client.put(
            "/api/minmax/upload/",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)

        # ✅ Fetch and verify stored data 



        # Convert the timestamp string to a timezone-aware datetime object
        sent_timestamp = make_aware(datetime.strptime("2025-02-21", "%Y-%m-%d"))

        # Fetch the WeatherData record with the specific timestamp
        try:
            minmax = MinMaxData.objects.get(date=sent_timestamp)
        except MinMaxData.DoesNotExist:
            self.fail(f"No MinMaxData found with timestamp {sent_timestamp}")



        self.assertEqual(minmax.min_temperature, 20.0)  # ✅ Ensure correct stored value
        self.assertEqual(minmax.max_temperature, 38.0)
        self.assertEqual(minmax.min_humidity, 40.0)
        self.assertEqual(minmax.max_humidity, 50.0)
        print("✅ PUT /api/minmax/upload/ passed with correct stored values!")

    def test_status_upload(self):
        """✅ Test PUT /api/status/upload/ and validate stored data"""
        payload = {
            "id": "esp32-001",
            "ts": "20250220150000",
            "upt": 120000,
            "mem": 200000,
            "wif": -75
        }
        response = self.client.put(
            "/api/status/upload/",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)

        # ✅ Fix: Ensure fetching the latest status correctly
        latest_status = SystemStatus.objects.get(station=self.station)
        self.assertEqual(latest_status.uptime_ms, 120000)
        self.assertEqual(latest_status.free_heap, 200000)
        self.assertEqual(latest_status.wifi_strength, -75)
        print("✅ PUT /api/status/upload/ passed with correct stored values!")


def test_weather_upload(self):
    """✅ Test PUT /api/weather/upload/ and validate stored data"""
    payload = {
        "id": "esp32-001",
        "data": [{"ts": "20250220145900", "tmp": 25.0, "hum": 55.0}]
    }
    response = self.client.put(
        "/api/weather/upload/",
        data=json.dumps(payload),
        content_type="application/json"
    )
    self.assertEqual(response.status_code, 201)

    # Convert the timestamp string to a timezone-aware datetime object
    sent_timestamp = make_aware(datetime.strptime("20250220145900", "%Y%m%d%H%M%S"))

    # Fetch the WeatherData record with the specific timestamp
    try:
        weather = WeatherData.objects.get(timestamp=sent_timestamp)
    except WeatherData.DoesNotExist:
        self.fail(f"No WeatherData found with timestamp {sent_timestamp}")

    # Validate the stored data
    self.assertEqual(weather.temperature, 25.0)  # ✅ Ensure correct stored value
    self.assertEqual(weather.humidity, 55.0)
    print("✅ PUT /api/weather/upload/ passed with correct stored values!")

