# Use Wokwi Locally on VS Code

## Install Arduino CLI

In the repository `<TOOL-PATH>` where you store your tools, run:
```bash
curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh
```

Update `PATH` in `.bashrc`:
```bash
export PATH=$PATH:<TOOL-PATH>
```

## Project Structure

Create the following structure for your files:
```plaintext
<my-project-path>/esp32-meteo/
├── diagram.json         # Defines the hardware (ESP32, DHT22, OLED, etc.)
├── wokwi.toml          # Specifies firmware and ELF paths for Wokwi simulation
├── build/              # Contains compiled output files (created after compiling)
│   ├── esp32-meteo.ino.bin  # Compiled firmware for flashing or simulation
│   └── esp32-meteo.ino.elf  # Executable with debugging info
└── esp32-meteo.ino     # The main Arduino code
```

- Copy the `diagram.json` file from Wokwi's web simulation to `<my-project-path>/esp32-meteo/`.
- Copy the code to `esp32-meteo.ino` (Arduino CLI requires a `.ino` file with the same name as the project directory).
- Create a `wokwi.toml` file with the following content:

```toml
[wokwi]
version = 1
firmware = "build/esp32-meteo.ino.bin"
elf = "build/esp32-meteo.ino.elf"
```

After compilation, the `firmware.bin` and `firmware.elf` files will be created inside `build/`.

## Install Wokwi Locally on VS Code

Wokwi offers a free extension for Visual Studio Code that lets you run Wokwi simulations locally.

### Steps to Set Up Wokwi in VS Code:
1. Install [Visual Studio Code](https://code.visualstudio.com/).
2. Install the Wokwi Extension for VS Code:
   - Open VS Code and go to the Extensions tab (left sidebar).
   - Search for "Wokwi Simulator" and click **Install**.
3. Activate your Wokwi license:
   ```
   CTRL + SHIFT + P → "Wokwi: Request a License"
   CTRL + SHIFT + P → "Wokwi: Manually Enter License Key"
   ```

## Install the ESP32 Core for Arduino CLI

Run the following commands to install the required core and libraries:
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

### Verify Installed Libraries
Run the following command to list all installed libraries:
```bash
arduino-cli lib list
```

## Compile the ESP32 Wokwi Project

```bash
arduino-cli compile --fqbn esp32:esp32:esp32 --output-dir build esp32-meteo.ino
```

## Execute and Test

### Simulate in VS Code (Wokwi)
Run your Wokwi simulation in VS Code with:
```bash
wokwi-server --project .
```

### Start Simulation Directly from VS Code:
1. Open VS Code in the project directory.
2. Press `CTRL + SHIFT + P` → "Wokwi: Start Simulator".

---

# Mock Server to Emulate the ESP32 Webserver

## Setting Up the Environment
```bash
mkdir flask_mock_server
cd flask_mock_server
python3 -m venv venv
source venv/bin/activate  # (Linux/macOS)
venv\Scripts\activate    # (Windows)
pip install flask
```
Create a new Python script:
```bash
touch mok_esp32_meteo_server.py
```
Update `mok_esp32_meteo_server.py` with the provided example.

## Start and Call the Mock Webserver
Run the mock server with:
```bash
python mok_esp32_meteo_server.py
```

Flask will start on `http://0.0.0.0:5000/`. You should see output like:
```plaintext
Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
```

## Accessing Your Endpoints

After starting the server, access the mock API using:

### Browser
```plaintext
http://localhost:5000/status
http://localhost:5000/lastreport
http://localhost:5000/maximahistory
http://localhost:5000/history
```

### cURL (Linux/macOS/Windows)
```bash
curl http://localhost:5000/status
curl http://localhost:5000/lastreport
curl http://localhost:5000/maximahistory
curl http://localhost:5000/history
```

### From an Android App
Find your PC’s IP address using:
```bash
ip a | grep inet  # Linux/macOS
ipconfig          # Windows
```

Call the API from your Android app by replacing `localhost` with your PC's IP:
```plaintext
http://<YOUR_PC_IP>:5000/status
```

