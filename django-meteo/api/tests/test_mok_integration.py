import unittest
import requests
import subprocess
import time

DJANGO_API_BASE = "http://127.0.0.1:8000/api"
ESP32_MOCK_BASE = "http://127.0.0.1:5000"

class ESP32MockIntegrationTests(unittest.TestCase):
    """✅ Integration test for ESP32 Mock Server"""

    @classmethod
    def setUpClass(cls):
        """🚀 Start Django and ESP32 Mock Server"""
        print("🚀 Starting Django and ESP32 Mock Server...")
        
        # ✅ Start Django in background
        cls.django_process = subprocess.Popen(["python", "manage.py", "runserver"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(5)  # Give Django time to start

        # ✅ Start ESP32 mock
        cls.mock_process = subprocess.Popen(["python", "flask-mock-server/mock_esp32.py", "1"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(3)  # Give Flask time to start

    @classmethod
    def tearDownClass(cls):
        """🔴 Stop Django and ESP32 Mock Server"""
        print("🔴 Stopping servers...")
        cls.django_process.terminate()
        cls.mock_process.terminate()

    def test_mock_last_report(self):
        """✅ Test GET /api/lastreport/esp32-001/ from ESP32 Mock"""
        response = requests.get(f"{ESP32_MOCK_BASE}/api/lastreport/esp32-001/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("ts", response.json())

    def test_mock_minmax_history(self):
        """✅ Test GET /api/minmax/history/esp32-001/ from ESP32 Mock"""
        response = requests.get(f"{ESP32_MOCK_BASE}/api/minmax/history/esp32-001/")
        self.assertEqual(response.status_code, 200)

    def test_mock_status(self):
        """✅ Test GET /api/status/esp32-001/ from ESP32 Mock"""
        response = requests.get(f"{ESP32_MOCK_BASE}/api/status/esp32-001/")
        self.assertEqual(response.status_code, 200)

    def test_mock_sync(self):
        """✅ Test GET /api/sync/esp32-001/"""
        response = requests.get(f"{ESP32_MOCK_BASE}/api/sync/esp32-001/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("msg", response.json())

if __name__ == "__main__":
    unittest.main()
