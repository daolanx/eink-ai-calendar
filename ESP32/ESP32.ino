#include <Arduino.h>
#include <WiFi.h>
#include <esp_sleep.h>
#include <HTTPClient.h>
#include <stdlib.h>
#include <string.h>
#include "config.h"
#include "EInk.h"
#include "time.h"

#define MAX_WIFI_CONNECT_RETRY 20  /* Maximum number of WiFi connection retries */
#define US_TO_S_FACTOR 1000000     /* Conversion factor from microseconds to seconds */
#define TIME_TO_SLEEP (60 * 60 * 1) /* Time ESP32 will sleep (in seconds) - 1 hour */

#define NTP_SERVER "pool.ntp.org"   /* NTP server address */
#define GMT_OFFSET_SEC (8 * 3600)   /* GMT offset (in seconds) - UTC+8 */
#define DAYLIGHT_OFFSET_SEC 0       /* Daylight saving time offset (in seconds) */

void setup() {
    Serial.begin(115200);
    delay(1000);  // Give some time for serial to be ready
    Serial.println("ESP32 starting up...");

    if (!connectWiFi()) {
        Serial.println("Failed to connect to WiFi");
        return;
    }

    // Initialize and sync network time
    configTime(GMT_OFFSET_SEC, DAYLIGHT_OFFSET_SEC, NTP_SERVER);
    Serial.println("Waiting for time sync...");
    delay(3000);  // Give some time for time sync

    // Check if it's early morning or if it's a restart
    bool isEarly = isEarlyMorning();
    bool isPowerOn = isRestByPowerOn();
    if (isEarly || isPowerOn) {
        Serial.println("Updating E-Ink display. Reason: " + String(isEarly ? "Early morning" : "Restarted by power on"));
        updateEInk();
    } else {
        Serial.println("Skip E-Ink update. Reason: Not early morning and not restarted by power on");
    }

    // Set timer wakeup
    esp_sleep_enable_timer_wakeup((uint64_t)TIME_TO_SLEEP * US_TO_S_FACTOR);
    Serial.println("Setup ESP32 to sleep for " + String(TIME_TO_SLEEP) + " seconds");
    
    // Enter deep sleep
    Serial.println("Going to deep sleep now");
    esp_deep_sleep_start();
}

void loop() {
    // Loop function won't be executed in deep sleep mode
}

bool connectWiFi() {
    int wifi_connect_try = 0;
    WiFi.begin(ssid, password);
    Serial.println("Connecting to WiFi...");
    while (WiFi.status() != WL_CONNECTED && wifi_connect_try < MAX_WIFI_CONNECT_RETRY) {
        delay(500);
        Serial.print(".");
        wifi_connect_try++;
    }

    if (WiFi.status() == WL_CONNECTED) {
        Serial.print("Connected, IP address: ");
        Serial.println(WiFi.localIP());
        return true;
    } else {
        Serial.println("Failed to connect to WiFi");
        return false;
    }
}

bool isEarlyMorning() {
    struct tm timeinfo;
    if (!getLocalTime(&timeinfo)) {
        Serial.println("Failed to obtain time");
        return false;
    }
    Serial.println(&timeinfo, "%A, %B %d %Y %H:%M:%S");
    Serial.println("Current hour: " + String(timeinfo.tm_hour));
    // Check if it's early morning
    bool isEarlyMorning = timeinfo.tm_hour == 0;
    Serial.println("isEarlyMorning: " + String(isEarlyMorning));
    return isEarlyMorning;
}

bool isRestByPowerOn() {
    esp_reset_reason_t reset_reason = esp_reset_reason();
    Serial.println("Reset reason: " + String(reset_reason));
    return (reset_reason == ESP_RST_POWERON);
}

void updateEInk() {
    String req = String(host) + "/bytes";
    HTTPClient http;
    http.begin(req);
    
    http.setTimeout(60000);
    
    Serial.println("Sending HTTP request to: " + req);
    int httpCode = http.GET();
    Serial.println("HTTP response code: " + String(httpCode));
    
    int len = http.getSize();
    Serial.println("Response size: " + String(len));
    
    if (httpCode == HTTP_CODE_OK && len == IMAGE_SIZE) {
        // ... (rest of the updateEInk function remains the same)
        DEV_Module_Init();
        EPD_5IN65F_Init();
        delay(10);
        EPD_5IN65F_Display_begin();
        uint8_t temp_buff[TEMP_BUFF_SIZE] = {0};
        int offset = 0;
        WiFiClient *stream = http.getStreamPtr();
        stream->setTimeout(60000);
        while (http.connected() && (offset < IMAGE_SIZE)) {
            size_t size = stream->available();
            if (size) {
                int c = stream->readBytes(temp_buff, ((size > sizeof(temp_buff)) ? sizeof(temp_buff) : size));
                for (int i = 0; i < c; i++) {
                    EPD_5IN65F_SendData(temp_buff[i]); // Send received data
                }
                offset += c;
                Serial.println("received: " + String(offset) + "/" + String(IMAGE_SIZE));
                delay(10);
            }
        }
        delay(100);
        EPD_5IN65F_Display_end();
        EPD_5IN65F_Sleep();
        Serial.println("update E-Ink done");
    } else {
        Serial.println("update E-Ink failed. HTTP code: " + String(httpCode) + ", Length: " + String(len));
    }
    http.end();
}
