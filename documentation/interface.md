All extern interfaces in the project are defined here.
- ESP32 API Interface 
- Django API Interface 


**📌 Extra Documentation**  
- 🛠️ [Testing Instructions](documentation/test.md) – Steps to verify Django server functionality.  



 
# **ESP32 API Interface Definition**

## **📌 Overview**
The ESP32 interfaces with:
- **OLED Display** (Local output - not defined in API)
- **Android App** (GET requests to fetch weather data)
- **Django Backend** (Synchronizes weather data via PUT requests)

The ESP32 runs a **WebServer** that serves data for the **Android App** and **Django Server**.

To **simplify API design**, the ESP32 **uses the same JSON format as Django API**.  
➡️ **Refer to the chapter**: **📡 Django API Interface Definition** for full details.

---

## **📌 WebServer API Endpoints (Served by ESP32)**  
The ESP32 provides **local API endpoints** (accessible via the Android app or Django).

| **Endpoint**               | **Method** | **Description** |
|---------------------------|-----------|----------------|
| `/api/status`             | `GET`     | Get system status from ESP32 |
| `/api/lastreport`         | `GET`     | Get the latest weather report |
| `/api/history`            | `GET`     | Get historical weather data |
| `/api/minmax/history`     | `GET`     | Get min/max temperature & humidity |
| `/api/sync`               | `GET`     | Manually trigger Django synchronization |

---

## **📌 ESP32 Synchronization Process**
ESP32 synchronizes with the **Django VPS** every hour (or when triggered via `/api/sync`).

#### **🔄 Steps:**
1️⃣ **Fetch `/api/lastupdate/<id>/`** → Get last recorded timestamp from Django.  
2️⃣ **Prepare data for upload** → Weather history & min/max data **since last update**.  
3️⃣ **Send `/api/weather/upload/`** → Upload **batch weather data**.  
4️⃣ **Send `/api/minmax/upload/`** → Upload **batch min/max records**.  
5️⃣ **Send `/api/status/upload/`** → Upload **latest system status**.  
6️⃣ **Repeat every hour** (or on demand via `/api/sync`).  

✅ **Batch uploads minimize network usage.**  
✅ **Short JSON keys reduce payload size.**  

---

## **📌 JSON Format for `GET` Requests (ESP32 WebServer)**
ESP32 provides **local JSON responses** matching Django format.

### **📌 `/api/status`**
```json
{
  "id": "esp32-001",
  "upt": 100000,
  "mem": 223484,
  "wif": -89
}
```

### **📌 `/api/lastreport`**
```json
{
  "id": "esp32-001",
  "ts": "2025-02-20 13:00:00",
  "tmp": 24.7,
  "hum": 55.2
}
```

### **📌 `/api/history`**
```json
{
  "id": "esp32-001",
  "history": [
    {"ts": "2025-02-20 10:00:00", "tmp": 22.5, "hum": 60.0},
    {"ts": "2025-02-20 11:00:00", "tmp": 23.0, "hum": 58.5}
  ]
}
```

### **📌 `/api/minmax/history`**
```json
{
  "id": "esp32-001",
  "history": [
    {"dt": "2025-02-19", "tmin": 18.3, "tmax": 39.4, "hmin": 37.1, "hmax": 43.9},
    {"dt": "2025-02-18", "tmin": 17.5, "tmax": 38.2, "hmin": 35.4, "hmax": 42.7}
  ]
}
```

### **📌 `/api/sync`**
```json
{
  "msg": "Sync process started"
}
```

---

## **📌 JSON Format for `PUT` Requests (ESP32 → Django)**
ESP32 pushes data to Django in **batch format**.

### **📌 `/api/weather/upload/`**
```json
{
  "id": "esp32-001",
  "data": [
    {"ts": "2025-02-20 10:00:00", "tmp": 22.5, "hum": 60.0},
    {"ts": "2025-02-20 11:00:00", "tmp": 23.0, "hum": 58.5}
  ]
}
```

### **📌 `/api/minmax/upload/`**
```json
{
  "id": "esp32-001",
  "data": [
    {"dt": "2025-02-19", "tmin": 18.3, "tmax": 39.4, "hmin": 37.1, "hmax": 43.9}
  ]
}
```

### **📌 `/api/status/upload/`**
```json
{
  "id": "esp32-001",
  "ts": "2025-02-20 12:00:00",
  "upt": 100000,
  "mem": 223484,
  "wif": -89
}
```
 


# **📡 Django API Interface Definition**  


---

## **📌 Overview of API Endpoints**  

The Django backend provides **RESTful API endpoints** for **ESP32 stations and the Android app**.  

---

## **🔹 `PUT` Requests (ESP32 → Django)**  
ESP32 devices send **weather data and system status** to Django.  

| **Endpoint**                 | **Method** | **Description** |
|-----------------------------|-----------|----------------|
| `/api/weather/upload/`      | `PUT`     | ESP32 sends multiple temperature & humidity readings |
| `/api/minmax/upload/`       | `PUT`     | ESP32 sends multiple min/max temperature & humidity records |
| `/api/status/upload/`       | `PUT`     | ESP32 sends system status (latest only) |

---

## **🔹 `GET` Requests (Android App & ESP32 → Django)**  
The **Android app and ESP32** retrieve weather data from Django.  

| **Endpoint**                   | **Method** | **Description** |
|---------------------------------|-----------|----------------|
| `/api/stations/`               | `GET`     | Get a list of registered ESP32 stations |
| `/api/status/<id>/`            | `GET`     | Get system status of a specific ESP32 station |
| `/api/lastreport/<id>/`        | `GET`     | Get the latest weather report for a station |
| `/api/history/<id>/`           | `GET`     | Get historical weather data for a station |
| `/api/minmax/history/<id>/`    | `GET`     | Get min/max temperature & humidity for the last 7 days |
| `/api/lastupdate/<id>/`        | `GET`     | Get the last update timestamp for a station | 

---

## **📌 JSON Format for `PUT /api/weather/upload/` (Batch Upload)**
ESP32 uploads **multiple weather readings**.  

#### **🔹 Request Example:**
```json
{
  "id": "esp32-001",
  "data": [
    {"ts": "2025-02-20 10:00:00", "tmp": 22.5, "hum": 60.0},
    {"ts": "2025-02-20 11:00:00", "tmp": 23.0, "hum": 58.5},
    {"ts": "2025-02-20 12:00:00", "tmp": 24.1, "hum": 57.0}
  ]
}
```
#### **🔹 Response Example:**
```json
{
  "msg": "Weather data received",
  "count": 3
}
```

---

## **📌 JSON Format for `PUT /api/minmax/upload/` (Batch Upload)**
ESP32 uploads **multiple min/max records**.  

#### **🔹 Request Example:**
```json
{
  "id": "esp32-001",
  "data": [
    {"dt": "2025-02-19", "tmin": 18.3, "tmax": 39.4, "hmin": 37.1, "hmax": 43.9},
    {"dt": "2025-02-18", "tmin": 17.5, "tmax": 38.2, "hmin": 35.4, "hmax": 42.7}
  ]
}
```
#### **🔹 Response Example:**
```json
{
  "msg": "Min/Max data received",
  "count": 2
}
```

---

## **📌 JSON Format for `PUT /api/status/upload/`**
ESP32 uploads **latest system status**.  

#### **🔹 Request Example:**
```json
{
  "id": "esp32-001",
  "ts": "2025-02-20 12:00:00",
  "upt": 100000,
  "mem": 223484,
  "wif": -89
}
```
#### **🔹 Response Example:**
```json
{
  "msg": "System status updated"
}
```

---

## **📌 JSON Format for `GET /api/stations/`**
Retrieve **list of stations**.  

#### **🔹 Response Example:**
```json
{
  "stations": [
    {"id": "esp32-001", "name": "Outdoor Sensor", "loc": "Garden", "created": "2025-02-15 10:30:00"},
    {"id": "esp32-002", "name": "Indoor Sensor", "loc": "Living Room", "created": "2025-02-16 14:15:00"}
  ]
}
```

---

## **📌 JSON Format for `GET /api/status/<id>/`**
Retrieve **system status**.  

#### **🔹 Response Example:**
```json
{
  "id": "esp32-001",
  "upt": 100000,
  "mem": 223484,
  "wif": -89
}
```

---

## **📌 JSON Format for `GET /api/lastreport/<id>/`**
Retrieve **latest weather report**.  

#### **🔹 Response Example:**
```json
{
  "id": "esp32-001",
  "tmp": 24.7,
  "hum": 55.2,
  "ts": "2025-02-20 13:00:00"
}
```

---

## **📌 JSON Format for `GET /api/history/<id>/`**
Retrieve **historical weather data**.  

#### **🔹 Response Example:**
```json
{
  "id": "esp32-001",
  "history": [
    {"ts": "2025-02-20 10:00:00", "tmp": 22.5, "hum": 60.0},
    {"ts": "2025-02-20 11:00:00", "tmp": 23.0, "hum": 58.5},
    {"ts": "2025-02-20 12:00:00", "tmp": 24.1, "hum": 57.0}
  ]
}
```

---

## **📌 JSON Format for `GET /api/lastupdate/<id>/`**
ESP32 **fetches last update timestamp** to determine **new data to send**.  

#### **🔹 Response Example:**
```json
{
  "ts": "2025-02-20 12:00:00"
}
```

