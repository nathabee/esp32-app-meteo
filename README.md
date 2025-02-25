# **ESP32 Meteo Station: Full Stack Project**

## **🌦️ Presentation: ESP32 Weather Station Project**

After purchasing the **Freenove Ultimate Starter Kit** with the **ESP32-WROVER**—a powerful ESP32-based development board—I decided to embark on an exciting project: **building a Weather Station**.

This project transforms the **ESP32 into a weather monitoring device** capable of measuring **temperature** and **humidity**. The ESP32 acts as a **web server**, delivering real-time data in **JSON format** through API routes like `/lastreport` and `/status`. This allows users to access **live weather information** from anywhere on the network.

In addition to serving data via a web server, the **readings will be displayed on a 128x64 OLED screen**. The project also includes an **Android app built using MIT App Inventor**, which fetches and displays data from the ESP32’s API, providing a **clean, user-friendly interface**.

### **☁️ Cloud Integration**
Each **ESP32 Weather Station** will **store its data permanently on a Django server** in the cloud.  
All **registered weather stations** will upload their data to the **Django backend**, ensuring reliable storage and easy access.

### **📱 Project Architecture**
This project integrates the following components:
✅ **ESP32 Weather Station** for data collection (hardware & firmware, tested with Wokwi)  
✅ **Django backend** to store and serve data from a VPS (with SQLite database)  
✅ **Android app** for data visualization (developed with MIT App Inventor)  
✅ **Flask mock server** to emulate ESP32 behavior during development  

---

```mermaid
graph TD
  subgraph Cloud
    Database["Database (SQLite)"]
    DjangoServer["🌐 Cloud-Based Django Server"]
  end

  subgraph Remote Weather Stations
    RemoteStation1["🌡️ Remote Weather Station 1"]
    RemoteStation2["🌡️ Remote Weather Station 2"]
  end

  subgraph Local Network
    HandyDevice["📱 Device (Handy)"]
    LocalWeatherStation["🌦️ Local Weather Station"]
  end

  %% Data Flow %%
  RemoteStation1 -- "PUT: Upload Data" --> DjangoServer
  RemoteStation2 -- "PUT: Upload Data" --> DjangoServer
  Database -- "retrieve Data" --> DjangoServer
  LocalWeatherStation -- "PUT: Upload Data" --> DjangoServer
  DjangoServer -- "GET: Config/Commands" --> RemoteStation1
  DjangoServer -- "GET: Config/Commands" --> RemoteStation2
  DjangoServer -- "Save Data" --> Database
  DjangoServer -- "GET: Config/Commands" --> LocalWeatherStation
  HandyDevice -- "GET: Fetch Reports/Data" --> DjangoServer
  HandyDevice -- "GET: Direct Query" --> LocalWeatherStation
```
---
 
## **📌 Table of Contents**
1. [Presentation](#1-presentation)
2. [ESP32 Weather Station](#2-esp32-weather-station)
3. [Mock Server to Emulate the ESP32 Webserver](#3-mock-server-to-emulate-the-esp32-webserver)
4. [MIT App Inventor App](#4-mit-app-inventor-app)
5. [Django VPS Backend](#5-django-vps-backend)
7. [Interface & Test](#interface-and-tests)
 
---
 

# **1. Presentation**
This project is a **complete IoT-based weather station** that:
- **Measures** temperature & humidity using an **ESP32-based circuit**.
- **Sends data** to a **Django backend** for storage & processing.
- **Retrieves & displays** weather data using an **Android app** and an **OLED display** on the ESP32.

The system supports **multiple ESP32 weather stations**, a **Django backend running on a VPS**, and a **mobile frontend via an Android app**.

### **🔹 Project Components**
This project includes:
- **ESP32 Firmware**: Code for the ESP32 circuit, including **Wokwi simulation** and **Arduino CLI** compatibility.
- **Android App**: A mobile frontend, developed with **MIT App Inventor**, for displaying weather data.
- **Mock Server**: A Flask-based server to **simulate multiple ESP32 devices** for testing.
- **Django Backend**: A Python-based **Django server** (using **SQLite**) that stores weather data from multiple ESP32 stations and serves it to the app.

### **🔹 Key Features**
✅ **ESP32 Simulation with Wokwi** – Test the ESP32 code without real hardware.  
✅ **Django Backend on VPS** – Stores and serves weather data from multiple ESP32 stations.  
✅ **Android App (MIT App Inventor)** – Fetches and displays real-time weather data.  
✅ **ESP32 OLED Display** – Locally displays weather data on the ESP32 itself.  
✅ **Mock Server (Flask)** – Simulates ESP32 behavior for testing without physical hardware.  

### **🔹 External References**
- **ESP32 Hardware Simulation:** [Wokwi Simulator](https://wokwi.com/)    !!!!!!!!!!!To be done Need to be published
- **MIT App Development:** [MIT App Inventor](https://appinventor.mit.edu/)   !!!!!!!!!!!To be done Need to be published
- **Instructable:** !!!!!!!!!!!To be done Need to be published
 
---

# **2. ESP32 Weather Station**


 Use Wokwi Locally on VS Code
## **🔹 Install Arduino CLI**
In your **tools directory**, run:
```bash
curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh
```
Update **`PATH`** in `.bashrc`:
```bash
export PATH=$PATH:<TOOL-PATH>
```

---

## **🔹 Project Structure**
```
<my-project-path>/esp32-meteo/
├── diagram.json      # Defines ESP32 hardware setup
├── wokwi.toml       # Specifies firmware & ELF paths for Wokwi
├── build/           # Compiled output files (after compilation)
│   ├── esp32-meteo.ino.bin  # Compiled firmware
│   ├── esp32-meteo.ino.elf  # Executable with debugging info
└── esp32-meteo.ino  # Main Arduino code
```
✅ **Copy `diagram.json` & code from Wokwi to your local project.**

---

## **🔹 Install Wokwi on VS Code**
1. Install [Visual Studio Code](https://code.visualstudio.com/).
2. Install the **Wokwi Extension**:
   - Open **Extensions Tab** (`CTRL + SHIFT + X`).
   - Search for **"Wokwi Simulator"** and click **Install**.
3. Activate the Wokwi License:
   ```bash
   CTRL + SHIFT + P → "Wokwi: Request a License"
   CTRL + SHIFT + P → "Wokwi: Manually Enter License Key"
   ```

---

## **🔹 Install ESP32 Core & Required Libraries**
```bash
arduino-cli core update-index
arduino-cli core install esp32:esp32
arduino-cli lib install "Adafruit GFX Library"
arduino-cli lib install "Adafruit SSD1306"
arduino-cli lib install "DHT sensor library"
arduino-cli lib install "ArduinoJson"
arduino-cli lib install "Time"
arduino-cli lib install "NTPClient"
```

✅ **Verify installed libraries:**
```bash
arduino-cli lib list
```

---

## **🔹 Compile & Run ESP32 Wokwi Simulation**
```bash
arduino-cli compile --fqbn esp32:esp32:esp32 --output-dir build esp32-meteo.ino
```
To **run the simulation** in VS Code:
```bash
wokwi-server --project .
```

---

# **3. Mock Server to Emulate the ESP32 Webserver**
During development, you can **emulate the ESP32 Webserver** using a Flask app.

### **🔹 Setup Flask Mock Server**
```bash
mkdir flask_mock_server
cd flask_mock_server

python3 -m venv ~/coding/project/esp32-app-meteo/flask-mock-server/venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate    # Windows
pip install -r requirements.txt

# pip install flask requests
# pip freeze > requirements.txt

```
Create the server script:
```bash
touch mok_esp32_meteo_server.py
```
Start the mock server:
```bash
python mok_esp32_meteo_server.py
```
✅ The server will run on:
```
http://0.0.0.0:5000/
```
✅ Test it:
```bash 
curl -X GET http://127.0.0.1:5000/api/status/esp32-001/
curl -X GET http://127.0.0.1:5000/api/lastreport/esp32-001/
curl -X GET http://127.0.0.1:5000/api/history/esp32-001/
curl -X GET http://127.0.0.1:5000/api/minmax/history/esp32-001/
curl -X GET http://127.0.0.1:5000/api/lastupdate/esp32-001/
curl -X GET http://127.0.0.1:5000/api/sync/esp32-001/

```

---



# **4. MIT App Inventor App**
The code of the project is stored in the **`mit-app-inventor`** directory as a **`.aia`** file.

## ** Description**
With **MIT App Inventor**, we create an Android app capable of displaying weather data retrieved from a **web server**.  
The server's **IP is configurable**, and data is retrieved in **JSON format**.

### **🌐 The App Interfaces With:**
✅ **ESP32 Circuit Board** – Emulating a web server in the **local network** (to be implemented).  
✅ **Django Meteo Interface** – Hosted on a **VPS**, serving as the main backend.

---

## **📂 Access the Project Code**
### **🔹 Reopen the Project from the `.aia` File (Stored in GitHub)**
1. Open **[MIT App Inventor](https://appinventor.mit.edu/)**  
2. Go to **Projects > Import project (.aia) from my computer**  
3. Select the **`.aia`** file from your GitHub repository  
4. Continue development 🚀  

### **🔹 Export the MIT App Inventor Project**
1. Open **MIT App Inventor**  
2. Go to **Projects > Export selected project (.aia)**  
3. Save the `.aia` file on your computer  
4. Move the file into the **local GitHub repository**  
5. Commit & push it to GitHub:
   ```sh
   git add mit-app-inventor/MyApp.aia
   git commit -m "Added latest MIT App Inventor project"
   git push origin main
   ```

---
Here's your updated **README** for the Django VPS Backend, including details about the API endpoints, testing, and ensuring smooth integration with ESP32 and the Android app.

---

# **5. Django VPS Backend**
## **🌍 Overview**
The **Django Meteo Backend** is responsible for **storing and serving weather data** collected from multiple ESP32 stations.

### **How It Works**
✅ **ESP32 stations synchronize data** with Django:  
   - The ESP32 **requests the last update timestamp** from Django.  
   - It **sends all new weather data** recorded since the last update.  
   - Django **saves the data** and **updates the last timestamp** for the ESP32 station.

✅ **Django serves weather data** to external applications:  
   - The **Android app fetches the list of stations** from Django.  
   - The app **retrieves weather data for a specific station** based on a time range.  
   - Data is formatted in **JSON** for easy integration.

---

## **Installation & Setup**
### **1️⃣ Clone the Django Meteo Code from GitHub**
```sh
git clone https://github.com/YOUR_GITHUB_USERNAME/esp32-app-meteo.git
cd esp32-app-meteo/django-meteo
```
 
### **2️⃣ Run the Setup Script**
```sh
chmod +x ./scripts/setup_production.sh
./scripts/setup_production.sh
```
🚀 **This script will:**
- ✅ **Create a virtual environment** (if it doesn't exist).
- ✅ **Activate the virtual environment**.
- ✅ **Install dependencies** (`pip install -r requirements.txt`).
- ✅ **Run database migrations** (`python manage.py migrate`).
- ✅ **Populate the database with fake ESP32 data** (`python scripts/populate_fake_data.py`).

---

### **3️⃣ Verify Installation**
Run the test script:
```sh
./scripts/test_installation.sh
```
✅ **This script checks:**
- That **Python and the virtual environment** are properly set up.
- That **database migrations** were applied correctly.
- That **fake ESP32 data** was inserted successfully.

---

### **4️⃣ Start the Django Server for development**
Run the Django development server:
```sh
cd esp32-app-meteo/django-meteo
source venv/bin/activate
python manage.py runserver
```
✅ **This will:**
- Start the server at `http://127.0.0.1:8000/`
- Allow local testing of API endpoints.

The end point should be :
curl -X GET http://127.0.0.1:8000/api/stations/
curl -X GET http://127.0.0.1:8000/api/status/esp32-test-001/
curl -X GET http://127.0.0.1:8000/api/lastreport/esp32-test-001/
curl -X GET http://127.0.0.1:8000/api/history/esp32-test-001/
curl -X GET http://127.0.0.1:8000/api/minmax/history/esp32-test-001/
curl -X GET http://127.0.0.1:8000/api/lastupdate/esp32-test-001/
curl -X GET http://127.0.0.1:8000/api/sync/esp32-test-001/



### **5 Deployment on production with jenkins and github** 
 !!!!!!!!!!!To be done  



### **6 Start the Django Server for production** 
 !!!!!!!!!!!To be done  
---


## **📂 Project Structure**
```
django-meteo/
│── api/         (Django app)
│   ├── migrations/    (Database migration files)
│   ├── models.py      (Database schema)
│   ├── tests.py       (Unit tests)
│   ├── views.py       (API logic)
│── meteo/       (Django project, contains settings.py)
│   ├── settings.py    (Django configuration)
│   ├── urls.py        (API endpoints)
│── manage.py    (Django project entry point)
│── venv/        (Python virtual environment)
│── scripts/     (Custom project management tools)
│   ├── setup_production.sh   (Initial setup script)
│   ├── test_installation.sh  (Checks if installation was successful)
│   ├── populate_fake_data.py (Generates test ESP32 data)
```

# **Interface and Tests**
 

## 📌 Documentation
- 📖 [API Interface Definition](documentation/interface.md) – Details about API endpoints and JSON structures.
- 🛠️ [Testing Instructions](documentation/test.md) – Steps to verify Django server functionality.

---
