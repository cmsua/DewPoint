#include <M5Stack.h>
#include <Wire.h>

void setup() {
  M5.begin(true, false, true);
  M5.Power.begin();

  Serial.begin(115200);
  delay(500);

  Wire.begin(21, 22, 100000UL);  // SDA=21, SCL=22, 100kHz — Port A
  Serial.println("I2C scanner starting...");
}

void loop() {
  int found = 0;

  Serial.println("Scanning...");

  for (uint8_t addr = 1; addr < 127; addr++) {
    Wire.beginTransmission(addr);
    uint8_t error = Wire.endTransmission();

    if (error == 0) {
      Serial.printf("Device found at 0x%02X\n", addr);
      found++;
    }
  }

  if (found == 0) {
    Serial.println("No I2C devices found.");
  } else {
    Serial.printf("Scan done. %d device(s) found.\n", found);
  }

  Serial.println("----");
  delay(3000);
}