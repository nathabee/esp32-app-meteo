
# TEST 

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
python mok_esp32_meteo_server.py
``` 

### **3️⃣ Verify the Server is Running**
Once started, you should see output similar to:
```
 * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
```
You can now test it by opening your browser and visiting: 
- **Trigger sync:** [`http://127.0.0.1:5000/api/sync/`](http://127.0.0.1:5000/api/sync/)
- **ESP32 last report:** [`http://127.0.0.1:5000/api/lastreport`](http://127.0.0.1:5000/api/lastreport/esp32-001/)
 
### ** automatic testing the mok
```sh
cd flask-mok-server
python mok_mok_esp32_test.py
``` 





## **Test Django Server**
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
curl http://127.0.0.1:8000/api/maximahistory/esp32-001/
```

#### ✅ **ESP32 Uploads New Weather Data**
```sh
curl -X PUT http://127.0.0.1:8000/api/weather/upload/ \
     -H "Content-Type: application/json" \
     -d '{
           "station_id": "esp32-001",
           "timestamp": "2025-02-20T12:00:00Z",
           "temperature": 22.5,
           "humidity": 60.0
         }'
```

#### ✅ **ESP32 Uploads Min/Max Data**
```sh
curl -X PUT http://127.0.0.1:8000/api/minmax/upload/ \
     -H "Content-Type: application/json" \
     -d '{
           "station_id": "esp32-001",
           "date": "2025-02-20",
           "min_temperature": 18.3,
           "max_temperature": 39.4,
           "min_humidity": 37.1,
           "max_humidity": 43.9
         }'
```

#### ✅ **Django Calculates Min/Max Automatically**
```sh
curl http://127.0.0.1:8000/api/minmax/calculate/esp32-001/
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