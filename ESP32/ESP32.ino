#include <Arduino.h>
#include <WiFi.h>
#include <esp_sleep.h>
#include <HTTPClient.h>
#include <stdlib.h>
#include <string.h>
#include "config.h"
#include "EInk.h"
#include "time.h"

#define MAX_WIFI_CONNECT_RETRY 20
#define uS_TO_S_FACTOR 1000000  /* Conversion factor for micro seconds to seconds */
#define TIME_TO_SLEEP 60 * 60 * 1     /* Time ESP32 will go to sleep (in seconds) - 1 hour */

const char* ntpServer = "pool.ntp.org";
const long  gmtOffset_sec = 8 * 3600;
const int   daylightOffset_sec = 0;

void printLocalTime() {
    struct tm timeinfo;
    if (!getLocalTime(&timeinfo)) {
        Serial.println("Failed to obtain time");
        return;
    }
    Serial.println(&timeinfo, "%A, %B %d %Y %H:%M:%S");
}

bool isEarlyMorning() {
    struct tm timeinfo;
    if (!getLocalTime(&timeinfo)) {
        Serial.println("Failed to obtain time");
        return false;
    }
    Serial.print("Current hour: ");
    Serial.println(timeinfo.tm_hour);
    // 检查是否在凌晨时段
    return (timeinfo.tm_hour == 0);
}

void setup() {
    Serial.begin(115200);
    delay(1000);  // 给一些时间让串口准备好
    Serial.println("ESP32 starting up...");

    esp_sleep_wakeup_cause_t wakeup_reason;
    wakeup_reason = esp_sleep_get_wakeup_cause();
    switch(wakeup_reason)
    {
        case ESP_SLEEP_WAKEUP_EXT0 : Serial.println("Wakeup caused by external signal using RTC_IO"); break;
        case ESP_SLEEP_WAKEUP_EXT1 : Serial.println("Wakeup caused by external signal using RTC_CNTL"); break;
        case ESP_SLEEP_WAKEUP_TIMER : Serial.println("Wakeup caused by timer"); break;
        case ESP_SLEEP_WAKEUP_TOUCHPAD : Serial.println("Wakeup caused by touchpad"); break;
        case ESP_SLEEP_WAKEUP_ULP : Serial.println("Wakeup caused by ULP program"); break;
        default : Serial.println("Wakeup was not caused by deep sleep"); break;
    }

    // connect to wifi
    int wifi_connect_try = 0;
    WiFi.begin(ssid, password);
    Serial.println("Connecting to WiFi...");
    while (WiFi.status() != WL_CONNECTED && wifi_connect_try < MAX_WIFI_CONNECT_RETRY) {
        delay(500);
        Serial.print(".");
        wifi_connect_try++;
    }
    Serial.println();

    if (WiFi.status() == WL_CONNECTED) {
        Serial.print("Connected, IP address: ");
        Serial.println(WiFi.localIP());

        // 初始化并同步网络时间
        configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
        Serial.println("Waiting for time sync...");
        delay(2000);  // 给一些时间让时间同步

        // 打印本地时间
        printLocalTime();

        // 检查是否在凌晨时段
        if (isEarlyMorning()) {
            Serial.println("It's early morning. Updating E-Ink display.");
            updateEInk();
        } else {
            Serial.println("Not early morning. Skipping E-Ink update.");
        }

       
    } else {
        Serial.println("Failed to connect to WiFi");
    }

     // 断开 WiFi 连接
        WiFi.disconnect(true);

    // 设置定时唤醒
    esp_sleep_enable_timer_wakeup((uint64_t)TIME_TO_SLEEP * uS_TO_S_FACTOR);
    Serial.println("Setup ESP32 to sleep for " + String(TIME_TO_SLEEP) + " seconds");
    
    // 进入深度睡眠
    Serial.println("Going to deep sleep now");
    esp_deep_sleep_start();
}

void loop() {
}

void updateEInk() {
    String req = (String)host + "/bytes";
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
        while (http.connected() && (offset < IMAGE_SIZE)) 
        {
          size_t size = stream->available();
          if (size)
          {
                int c = stream->readBytes(temp_buff, ((size > sizeof(temp_buff)) ? sizeof(temp_buff) : size));
                for (int i = 0; i < c; i++)
                {
                    EPD_5IN65F_SendData(temp_buff[i]); // Send received data
                }
                offset += c;
                Serial.println("received: " + (String)offset + "/" + (String)IMAGE_SIZE);
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