#include <ESP8266WiFi.h>

const char* ssid = "vivekfiber";
const char* password = "Assam123";

int mq135Pin = A0;
int threshold = 300;  // Adjust this based on your ambient sensor readings

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting...");
  }
  Serial.println("Connected!");
}

void loop() {
  int airQuality = analogRead(mq135Pin);
  
  if (airQuality > threshold) {
    Serial.println("SMOKE");
  } else {
    Serial.println("CLEAR");
  }

  delay(1000);  // 1 reading per second (adjust delay as needed)
}
