
# automatic testing

a Django unit test automates API testing. This will allow you to validate that both the Django API and the mock ESP32 servers are working correctly.
 **Unit test for Django and ESP32 MOK are in `api/tests.py` **
 
### **✅ How to Run the Tests**


1️⃣ **Unit test Django API with test database**

**`test_django_api.py`** :
   - Uses Django's test database (no need for the mock).
   - Tests **6 GET** + **3 PUT** API endpoints.

```sh
python manage.py test api.tests.test_django_api
```

2️⃣.  **Integration test with ESP32 mock**

In this test we will use the esp32_mok to simulate a weather station in local
we will also use the django server in develeppement mode to make test

**`test_mock_integration.py`** :
   - Starts ESP32 mock server (`mock_esp32.py`).
   - Ensures the mock **communicates with Django**.
   - Tests **ESP32's GET requests** + **Sync test**.

 **Ensure the Flask Mock Servers are Running**
```sh
cd flask-mock-server
source venv/bin/activate
python mock_esp32.py 1 &
#python mock_esp32.py 2 &
#python mock_esp32.py 3 &
```

 **Ensure Django Server is Running ** 
```sh
source venv/bin/activate
python manage.py runserver
```

```sh
python api/tests/test_mock_integration.py
```


---

### **✅ What This Does**
- **Tests Django API**
  - Fetch **list of stations**
  - Fetch **latest weather report**
  - Upload **weather data**
  - Upload **min/max data**
  - Upload **status data**
  
- **Tests ESP32 Mock Server**
  - Fetch **ESP32 last report**
  - Trigger **sync process**


# TEST Details

## ** ESP32 MOK **
the ESP32 interface can be moked locally, using 

start the mok
run the test file


 I can't directly start the mock server for you, but you can start it yourself by running the Flask script on your local machine. Follow these steps:

### **1️⃣ Ensure Flask is Installed**
If you haven't installed Flask, install it with:
```sh
pip install flask
```

### **2️⃣ Run the Flask Mock Server**
Navigate to the directory where your Flask script is located and start the server:
```sh
cd flask-mok-server
python mock_esp32.py 1 &
python mock_esp32.py 2 &
python mock_esp32.py 3 &

``` 
This will start:

esp32-001 on port 5000
esp32-002 on port 5001
esp32-003 on port 5002

### **3️⃣ Verify the Server is Running**
Once started, you should see output similar to:
```
 * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
```
You can now test it by opening your browser and visiting: 
- **Trigger sync:** [`http://127.0.0.1:5000/api/sync/`](http://127.0.0.1:5000/api/sync/)
- **ESP32 last report:** [`http://127.0.0.1:5000/api/lastreport`](http://127.0.0.1:5000/api/lastreport/esp32-001/)
exemple test :
(http://127.0.0.1:5000/api/lastreport/esp32-001/)
(http://127.0.0.1:5001/api/lastreport/esp32-002/)
(http://127.0.0.1:5002/api/lastreport/esp32-003/)
(http://127.0.0.1:5000/api/sync/esp32-001/)

## **Test Django Server**

### **start django server** 

```sh 
cd esp32-app-meteo/django-meteo
source venv/bin/activate
python manage.py runserver
```

### **Test API Using `curl`**

#### ✅ **List Stations**
```sh
curl http://127.0.0.1:8000/api/stations/
```

#### ✅ **Get Latest Weather Report**
```sh
curl http://127.0.0.1:8000/api/lastreport/esp32-001/
```

#### ✅ **Get Weather History**
```sh
curl http://127.0.0.1:8000/api/history/esp32-001/
```

#### ✅ **Get Min/Max History**
```sh
curl http://127.0.0.1:8000/api/minmax/history/esp32-001/
```

#### ✅ **ESP32 Uploads New Weather Data**
```sh
curl -X PUT http://127.0.0.1:8000/api/weather/upload/ \
     -H "Content-Type: application/json" \
     -d '{
           "id": "esp32-outdoor",
           "data": [
             {"ts": "20250220120000", "tmp": 22.5, "hum": 60.0}
           ]
         }'

```

#### ✅ **ESP32 Uploads Min/Max Data**
```sh
curl -X PUT http://127.0.0.1:8000/api/minmax/upload/ \
     -H "Content-Type: application/json" \
     -d '{
           "id": "esp32-001",
           "dt": "20250220",
           "tmin": 18.3,
           "tmax": 39.4,
           "hmin": 37.1,
           "hmax": 43.9
         }'

```



#### ✅ **ESP32 Uploads Status Data**
```sh
curl -X PUT http://127.0.0.1:8000/api/status/upload/ \
     -H "Content-Type: application/json" \
     -d '{
           "id": "esp32-001",
           "ts": "20250220120000",
           "upt": 100000,
           "mem": 223484,
           "wif": -89
         }'


```


 
---

### **Test with Postman**
1️⃣ Open **Postman**  
2️⃣ Create a **new request**  
3️⃣ Set the **method** to `GET` or `PUT`  
4️⃣ Use one of the API URLs above  
5️⃣ Click **Send** to test responses  

---

### **Test with the Android App**
1️⃣ Ensure the Django server is **running on your VPS**.  
2️⃣ Update the **API base URL** in the Android app settings.  
3️⃣ Test retrieving weather data for different stations.  

---

### **Test ESP32 Communication**
1️⃣ Ensure ESP32 **is connected to the network**.  
2️⃣ Program ESP32 to **send weather data** to Django's API.  
3️⃣ Check Django logs to confirm **data is stored correctly**.  

---