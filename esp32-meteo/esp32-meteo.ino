#include <WiFi.h>
#include <WebServer.h>
#include <DHT.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <ArduinoJson.h>
#include <time.h>

#define DEBUGWOKWI true  // Set to true for debugging, false for production
 
#define BUTTON_PIN 4    // GPIO pin for the button
#define DHTPIN 15       // DHT Sensor
#define DHTTYPE DHT22   // DHT Sensor
#define MAX_RECORDS 336 // Store 7 days of data, 48 records per day

// Wi-Fi Credentials
const char *ssid = "Wokwi-GUEST";
const char *password = "";

// push button to display status
unsigned long lastButtonPress = 0; // Variable to store the time of the last button press
enum DisplayStatus
{
  LAST_REPORT,
  ESP32_STATUS,
  DEBUG_INFO,
  TEMP_HISTORY_PAGE1,
  TEMP_HISTORY_PAGE2,
  HUM_HISTORY_PAGE1,
  HUM_HISTORY_PAGE2
}; // Enum for display status
DisplayStatus currentStatus = LAST_REPORT; // Current status mode, default to LAST_REPORT

#define MAX_DAYS 8 // Store last 8 days' min/max

// history of weather
struct WeatherRecord
{
  time_t timestamp;
  float temperature;
  float humidity;
};

WeatherRecord history[MAX_RECORDS];
int currentRecordIndex = 0;
 
// Structure to hold daily min/max records
struct DailyRecord
{
  int year, month, day;
  float minTemp, maxTemp, minHum, maxHum;
};

DailyRecord dailyHistory[MAX_DAYS];
int historyStartIndex = 0; // Oldest entry
int historyCount = 0;      // Current record count

// humidity temperatur captor
DHT dht(DHTPIN, DHTTYPE);

// OLED Display
Adafruit_SSD1306 display(128, 64, &Wire, -1);

// Web Server
WebServer server(80);

float lastTemp = 0.0;
float lastHum = 0.0;
unsigned long lastTestRequest = 0;

// NTP server and timezone setup
const char *ntpServer = "pool.ntp.org";
const long gmtOffset_sec = 0;     // Adjust according to your timezone (GMT+0 in this case)
const int daylightOffset_sec = 0; // No daylight saving time offset

void setup()
{
  Serial.begin(115200);
  Serial.println("ESP32 Weather Station starting...");

  pinMode(BUTTON_PIN, INPUT);
  Serial.println("Button initialized.");

  dht.begin();
  Serial.println("DHT sensor initialized.");

  WiFi.begin(ssid, password);
  Serial.println("Connecting to WiFi...");
  int wifiAttempts = 0;
  while (WiFi.status() != WL_CONNECTED && wifiAttempts < 20)
  {
    delay(500);
    Serial.print(".");
    wifiAttempts++;
  }
  if (WiFi.status() == WL_CONNECTED)
  {
    Serial.println("\nConnected to WiFi!");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
  }
  else
  {
    Serial.println("\nFailed to connect to WiFi.");
  }

  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C))
  {
    Serial.println("SSD1306 allocation failed");
    while (true)
      delay(1000);
  }
  Serial.println("OLED Display initialized.");

  // NTP time sync
  Serial.println("Synchronizing time with NTP...");
  configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo))
  {
    Serial.println("Failed to obtain time.");
  }
  else
  {
    Serial.println(&timeinfo, "Time synced: %Y-%m-%d %H:%M:%S");
    /*
    char timeStringBuff[30];
    strftime(timeStringBuff, sizeof(timeStringBuff), "%Y-%m-%d %H:%M:%S", &timeinfo);
    Serial.printf("REDOTEST Time synced: %s\n", timeStringBuff);
    */
  }

  if (DEBUGWOKWI)
  {
    preloadFakeHistory();
    // Serial.println("DEBUG: Fake history loaded for testing.");
  }

  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.println("ESP32 Weather Station");
  display.display();

  server.on("/status", HTTP_GET, handleStatus);
  server.on("/lastreport", HTTP_GET, handleLastReport);
  server.on("/history", HTTP_GET, handleHistory);
  server.on("/maximahistory", HTTP_GET, handleMaximaHistory);
  server.begin();

  Serial.println("HTTP server started.");
}

void loop()
{
  server.handleClient();

  unsigned long now = millis();
  static unsigned long lastUpdate = 0;
  static float previousTemp = 0;
  static float previousHum = 0;
  bool displayNeedsUpdate = false;

  // Read DHT22 sensor data every 5 seconds
  if (now - lastUpdate >= 5000)
  {
    lastUpdate = now;

    time_t nowtimestamp = time(NULL);
    struct tm timeinfo;
    localtime_r(&nowtimestamp, &timeinfo);
  
    int year = timeinfo.tm_year + 1900;
    int month = timeinfo.tm_mon + 1;
    int day = timeinfo.tm_mday;

    float temp = dht.readTemperature();
    float hum = dht.readHumidity();

    if (!isnan(temp) && !isnan(hum))
    {

      updateDailyMinMax(year, month, day, temp, hum);
      if (temp != previousTemp || hum != previousHum)
      {
        previousTemp = temp;
        previousHum = hum; 
        displayCurrentStatus();
      }
    }
    else
    {
      Serial.println("Failed to read from DHT sensor.");
    }


  // handle history of th weather
  static unsigned long lastHistoryUpdate = 0;

  if (now - lastHistoryUpdate >= 60000)
  { // Every 30 minutes (1800000 ms)
    lastHistoryUpdate = now;

    
    updateHistory(nowtimestamp,temp, hum);
    }
  }

 


  // Check for button press
  handleButtonPress();

  // Simulate handleStatus call every 30 seconds for debugging
  if (DEBUGWOKWI && ((now - lastTestRequest) >= 100000))
  { 
    lastTestRequest = now;  
    simulateAllHandle();
  }
}
 

void handleButtonPress()
{
  static bool lastButtonState = digitalRead(BUTTON_PIN);
  static unsigned long pressStartTime = 0;
  static bool buttonPressed = false;
  bool currentButtonState = digitalRead(BUTTON_PIN);
  unsigned long now = millis();

  if (currentButtonState == lastButtonState)
  {
    return;
  }

  if (currentButtonState == HIGH && !buttonPressed)
  {
    pressStartTime = now;
    lastButtonState = HIGH;
    buttonPressed = true;
    return;
  }

  if (currentButtonState == LOW && buttonPressed)
  {
    unsigned long pressDuration = now - pressStartTime;

    if (pressDuration >= 1000)
    {
      handleLongPress();
    }
    else
    {
      handleShortPress();
    }

    lastButtonState = LOW;
    buttonPressed = false;
  }
}

void handleShortPress()
{
  if (DEBUGWOKWI)
  {
    Serial.println("DEBUG: Short press detected.");
  }

  // Cycle through the display modes in order
  currentStatus = static_cast<DisplayStatus>((currentStatus + 1) % 7);
  displayCurrentStatus();
}

void handleLongPress()
{
  if (DEBUGWOKWI)
  {
    Serial.println("DEBUG: Long press detected - Resetting to LAST_REPORT.");
  }

  // Reset to the first page
  currentStatus = LAST_REPORT;
  displayCurrentStatus();
}

void updateHistory(time_t nowtimestamp, float temp, float hum)
{
  // Store the data in the history buffer
  history[currentRecordIndex].timestamp = nowtimestamp;
  history[currentRecordIndex].temperature = temp;
  history[currentRecordIndex].humidity = hum;

  // Move the circular buffer index forward
  currentRecordIndex = (currentRecordIndex + 1) % MAX_RECORDS;

  if (DEBUGWOKWI)
  {
    Serial.printf("📝 Stored history[%d] -> %s | Temp: %.2f°C | Hum: %.2f%%\n",
                  currentRecordIndex,
                  formatTimestamp(nowtimestamp).c_str(),
                  temp, hum);
  }
}


void updateDailyMinMax(int year, int month, int day, float temp, float hum)
{

  /*
  time_t now = time(NULL);
  struct tm timeinfo;
  localtime_r(&now, &timeinfo);

  int year = timeinfo.tm_year + 1900;
  int month = timeinfo.tm_mon + 1;
  int day = timeinfo.tm_mday;
*/

  // 🔍 **Step 1: Check if a record for today already exists**
  for (int i = 0; i < historyCount; i++)
  {
    int index = (historyStartIndex + i) % MAX_DAYS; // Correct FIFO indexing
    if (dailyHistory[index].year == year &&
        dailyHistory[index].month == month &&
        dailyHistory[index].day == day)
    {
      // ✅ Update min/max **only if necessary** (avoids extra memory writes)
      bool updated = false;
      if (temp < dailyHistory[index].minTemp)
      {
        dailyHistory[index].minTemp = temp;
        updated = true;
      }
      if (temp > dailyHistory[index].maxTemp)
      {
        dailyHistory[index].maxTemp = temp;
        updated = true;
      }
      if (hum < dailyHistory[index].minHum)
      {
        dailyHistory[index].minHum = hum;
        updated = true;
      }
      if (hum > dailyHistory[index].maxHum)
      {
        dailyHistory[index].maxHum = hum;
        updated = true;
      }

      if (updated)
      {
        Serial.printf("✅ Updated history for %04d-%02d-%02d | Min: %.1f°C Max: %.1f°C | Min Hum: %.1f%% Max Hum: %.1f%%\n",
                      year, month, day,
                      dailyHistory[index].minTemp, dailyHistory[index].maxTemp,
                      dailyHistory[index].minHum, dailyHistory[index].maxHum);
      }
      return; // 🔄 **Exit because we updated today's record**
    }
  }

  // 🆕 **Step 2: No record for today → Add a new entry in FIFO**
  int newIndex;
  if (historyCount < MAX_DAYS)
  {
    newIndex = (historyStartIndex + historyCount) % MAX_DAYS; // Append to FIFO
    historyCount++;                                           // Increase count **only if there's space left**
  }
  else
  {
    // FIFO is full → **overwrite oldest record**
    newIndex = historyStartIndex;
    historyStartIndex = (historyStartIndex + 1) % MAX_DAYS; // Move FIFO start
  }

  // ✅ Store new record
  dailyHistory[newIndex] = {year, month, day, temp, temp, hum, hum};

  Serial.printf("🆕 Added new daily record for %04d-%02d-%02d | Temp: %.1f°C | Hum: %.1f%% (FIFO Index: %d, StartIndex: %d)\n",
                year, month, day, temp, hum, newIndex, historyStartIndex);
}

void displayCurrentStatus()
{
  display.clearDisplay();
  switch (currentStatus)
  {
  case LAST_REPORT:
    displayLastReport();
    break;
  case ESP32_STATUS:
    displayESP32Status();
    break;
  case DEBUG_INFO:
    displayDebugInfo();
    break;
  case TEMP_HISTORY_PAGE1:
    displayTemperatureHistory(1);
    break;
  case TEMP_HISTORY_PAGE2:
    displayTemperatureHistory(2);
    break;
  case HUM_HISTORY_PAGE1:
    displayHumidityHistory(1);
    break;
  case HUM_HISTORY_PAGE2:
    displayHumidityHistory(2);
    break;
  }
  display.display();
}


void displayLastReport()
{
  float temp = dht.readTemperature();
  float hum = dht.readHumidity();
  display.setCursor(0, 0);
  display.println("Last Report:");
  display.print("Temp: ");
  display.print(isnan(temp) ? "N/A" : String(temp) + " C");
  display.println();
  display.print("Humidity: ");
  display.print(isnan(hum) ? "N/A" : String(hum) + " %");
}

void displayESP32Status()
{
  display.setCursor(0, 0);
  display.println("ESP32 Status:");
  display.print("Uptime: ");
  display.print(millis() / 1000);
  display.println(" s");
  display.print("Free Heap: ");
  display.print(ESP.getFreeHeap());
  display.println(" bytes");
}

void displayDebugInfo()
{
  display.setCursor(0, 0);
  display.println("Debug Info:");
  display.print("IP: ");
  display.println(WiFi.localIP());
  display.print("WiFi RSSI: ");
  display.print(WiFi.RSSI());
  display.println(" dBm");
}


void displayTemperatureHistory(int page)
{

  if (DEBUGWOKWI)
  {
    Serial.println("🛠️ DEBUG: Printing history after preloading fake data...");
    printDailyHistory();

    Serial.flush(); // Ensure the log is fully written out
  }
 
  display.clearDisplay();
  display.setCursor(0, 0);
  display.println("Temp History:");

  if (historyCount == 0)
  {
    display.println("No Data");
    display.display();
    return;
  }

  int startIdx = (page == 1) ? historyCount - 1 : max(historyCount - 5, 0);
  int endIdx = max(startIdx - 4, -1);

  for (int i = startIdx; i > endIdx; i--)
  {
    int index = (historyStartIndex + i) % MAX_DAYS;
    display.printf("%02d/%02d %.1fC to %.1fC\n",
                   dailyHistory[index].day, dailyHistory[index].month,
                   dailyHistory[index].minTemp, dailyHistory[index].maxTemp);
  }

  display.display();
}


void displayHumidityHistory(int page)
{

  if (DEBUGWOKWI)
  {
    Serial.println("🛠️ DEBUG: Printing history after preloading fake data...");
    printDailyHistory();
    Serial.flush(); // Ensure the log is fully written out
  }

  display.clearDisplay();
  display.setCursor(0, 0);
  display.println("Hum History:");

  if (historyCount == 0)
  {
    display.println("No Data");
    display.display();
    return;
  }

  int startIdx = (page == 1) ? historyCount - 1 : max(historyCount - 5, 0);
  int endIdx = max(startIdx - 4, -1);

  for (int i = startIdx; i > endIdx; i--)
  {
    int index = (historyStartIndex + i) % MAX_DAYS;
    display.printf("%02d/%02d %.1f%% to %.1f%%\n",
                   dailyHistory[index].day, dailyHistory[index].month,
                   dailyHistory[index].minHum, dailyHistory[index].maxHum);
  }

  display.display();
}


// debug

void printDailyHistory()
{
  Serial.println("\n📜 ====== DAILY HISTORY (FIFO Order) ======");
  Serial.printf("🛠️ Start Index: %d | Total Records: %d / %d\n", historyStartIndex, historyCount, MAX_DAYS);

  if (historyCount == 0)
  {
    Serial.println("❌ No history records found!");
    return;
  }

  for (int i = 0; i < historyCount; i++)
  {
    int index = (historyStartIndex + i) % MAX_DAYS; // FIFO indexing

    Serial.printf("📅 Index: %2d (FIFO Pos: %2d) | Date: %04d-%02d-%02d | Min: %.1f°C Max: %.1f°C | Min Hum: %.1f%% Max Hum: %.1f%%\n",
                  index, i,
                  dailyHistory[index].year, dailyHistory[index].month, dailyHistory[index].day,
                  dailyHistory[index].minTemp, dailyHistory[index].maxTemp,
                  dailyHistory[index].minHum, dailyHistory[index].maxHum);
  }
  Serial.println("========================================\n");
}

String formatTimestamp(time_t timestamp)
{
  struct tm timeinfo;
  localtime_r(&timestamp, &timeinfo); // Convert time_t to tm structure

  char buffer[25]; // No need for static buffer, use local instead
  snprintf(buffer, sizeof(buffer), "%04d-%02d-%02d %02d:%02d:%02d",
           timeinfo.tm_year + 1900, timeinfo.tm_mon + 1, timeinfo.tm_mday,
           timeinfo.tm_hour, timeinfo.tm_min, timeinfo.tm_sec);

  return String(buffer); // Return a String (avoids static buffer corruption)
}

// Simulate the /status request internally
void simulateAllHandle()
{
  Serial.println("DEBUG: Simulating internal request to /status ");
  handleStatus(); // Call the /status handler directly
  Serial.println("DEBUG: Simulating internal request to /lastreport ");
  handleLastReport();
  Serial.println("DEBUG: Simulating internal request to /maximahistory ");
  handleMaximaHistory();
  Serial.println("DEBUG: Simulating internal request to /history ");
  handleHistory();
}

void handleStatus()
{
  if (DEBUGWOKWI)
  {
    Serial.println("DEBUG: handlestatus called");
  }

  StaticJsonDocument<300> json;
  json["uptime_ms"] = millis();
  json["free_heap"] = ESP.getFreeHeap();
  json["wifi_strength"] = WiFi.RSSI();
  json["status"] = "OK";

  String response;
  serializeJson(json, response);

  if (DEBUGWOKWI)
  {
    Serial.println("DEBUG /status Response: " + response);
    Serial.flush(); // Ensure the log is fully written out
  }

  server.send(200, "application/json", response);
}

void handleLastReport()
{
  float lastTemp = dht.readTemperature();
  float lastHum = dht.readHumidity();
  String response = "{";
  response += "\"temperature\":" + String(lastTemp) + ",";
  response += "\"humidity\":" + String(lastHum);
  response += "}";

  if (DEBUGWOKWI)
  {
    Serial.println("DEBUG Last Report Response: " + response);
    Serial.flush(); // Ensure the log is fully written out
  }

  server.send(200, "application/json", response);
}

void handleMaximaHistory()
{
  StaticJsonDocument<2048> json; // Adjusted based on expected data size
  JsonArray data = json.createNestedArray("history");

  // 🔄 Loop in reverse to show latest entries first
  for (int i = 0; i < historyCount; i++)
  {
    int index = (historyStartIndex + historyCount - 1 - i) % MAX_DAYS; // Reverse FIFO order

    JsonObject record = data.createNestedObject();
    record["date"] = String(dailyHistory[index].year) + "-" +
                     String(dailyHistory[index].month) + "-" +
                     String(dailyHistory[index].day);
    record["minTemp"] = dailyHistory[index].minTemp;
    record["maxTemp"] = dailyHistory[index].maxTemp;
    record["minHum"] = dailyHistory[index].minHum;
    record["maxHum"] = dailyHistory[index].maxHum;
  }

  String response;
  serializeJson(json, response);
  server.send(200, "application/json", response);

  if (DEBUGWOKWI)
  {
    Serial.println("DEBUG Last /maximahistory Response: " + response);
    Serial.flush(); // Ensure the log is fully written out
  }
}

void handleHistory()
{
  StaticJsonDocument<8192> json; // Increase if buffer overflow occurs
  JsonArray data = json.createNestedArray("history");

  for (int i = 0; i < MAX_RECORDS; i++)
  {
    int index = (currentRecordIndex + i) % MAX_RECORDS;
    if (history[index].timestamp != 0) // Skip uninitialized records
    {
      JsonObject record = data.createNestedObject();
      record["timestamp"] = formatTimestamp(history[index].timestamp);
      record["temperature"] = history[index].temperature;
      record["humidity"] = history[index].humidity;
    }
  }

  String response;
  serializeJson(json, response);
  server.send(200, "application/json", response);


  if (DEBUGWOKWI)
  {
    Serial.println("DEBUG /history Response: " + response);
    Serial.flush(); // Ensure the log is fully written out
  }
}

void preloadFakeHistory()
{
  Serial.println("📌 Preloading Fake Data...");

  time_t now = time(NULL); // Get current UNIX timestamp
  struct tm timeinfo;
  localtime_r(&now, &timeinfo); // Convert `now` to struct tm

  // ✅ Starting conditions
  float temp = 24.0, maxt = 24.0, mint = 24.0; // Initial temperature
  float hum = 40.0, maxh = 40.0, minh = 40.0;  // Initial humidity
  int lastDay = timeinfo.tm_mday; // Track day changes

  historyCount = MAX_DAYS;      // Reset daily history count
  historyStartIndex = MAX_DAYS ; // FIFO start index

  // ✅ Loop through `MAX_RECORDS` (30-min intervals)
  for (int i = 0; i < MAX_RECORDS; i++)
  {
    time_t recordTimestamp = now - (i * 1800); // Go back 30 min at a time
    localtime_r(&recordTimestamp, &timeinfo);  // Convert to struct tm

    // ✅ Adjust temperature & humidity based on time of day
    if (timeinfo.tm_hour > 4 && timeinfo.tm_hour <= 16) // Morning to 4 PM → Warm up
    {
      temp += (rand() % 20) / 10.0; // Increase 0 - 2°C
      hum += (rand() % 7) / 10.0;   // Increase 0 - 0.7%

      maxt = max(temp, maxt);
      maxh = max(hum, maxh);
    }
    else // Evening to 4 AM → Cool down
    {
      temp -= (rand() % 20) / 10.0; // Decrease 0 - 2°C
      hum -= (rand() % 7) / 10.0;   // Decrease 0 - 0.7%

      mint = min(temp, mint);
      minh = min(hum, minh);
    }

    // ✅ Store in `history[]` (detailed 30-min logs)
    history[MAX_RECORDS-1-i].timestamp = recordTimestamp;
    history[MAX_RECORDS-1-i].temperature = temp;
    history[MAX_RECORDS-1-i].humidity = hum;

    //Serial.printf("📝 History %d -> %04d-%02d-%02d %02d:%02d | Temp: %.1fC | Hum: %.1f%%\n",
    //              i, timeinfo.tm_year + 1900, timeinfo.tm_mon + 1, timeinfo.tm_mday,
    //              timeinfo.tm_hour, timeinfo.tm_min, temp, hum);

    // ✅ Detect day change → Store min/max in `dailyHistory[]`
    if ((timeinfo.tm_mday != lastDay) or (i == (MAX_RECORDS-1)))
    {
      // Calculate the FIFO index for the new daily entry 
      if (historyStartIndex > 0) { 
        historyStartIndex--; 
      }
      // ✅ Store in `dailyHistory[]`
      dailyHistory[historyStartIndex].year = timeinfo.tm_year + 1900;
      dailyHistory[historyStartIndex].month = timeinfo.tm_mon + 1;
      dailyHistory[historyStartIndex].day = lastDay;
      dailyHistory[historyStartIndex].minTemp = mint;
      dailyHistory[historyStartIndex].maxTemp = maxt;
      dailyHistory[historyStartIndex].minHum = minh;
      dailyHistory[historyStartIndex].maxHum = maxh;

      // Reset min/max for next day
      mint = maxt = temp;
      minh = maxh = hum;

      //Serial.printf("📅 DailyHistory[%d] -> %04d-%02d-%02d | Min: %.1fC Max: %.1fC | Min Hum: %.1f%% Max Hum: %.1f%%\n",
      //              index, dailyHistory[historyStartIndex].year, dailyHistory[historyStartIndex].month, dailyHistory[historyStartIndex].day,
      //              dailyHistory[historyStartIndex].minTemp, dailyHistory[historyStartIndex].maxTemp,
      //              dailyHistory[historyStartIndex].minHum, dailyHistory[historyStartIndex].maxHum);

      lastDay = timeinfo.tm_mday; // Update last tracked day
    }
  }

  // printDailyHistory();

  Serial.println("🎉 Fake history generation complete.");
}
