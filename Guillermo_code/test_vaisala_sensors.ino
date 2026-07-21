#include <M5Stack.h>
#include "MODULE_4_20MA.h"

MODULE_4_20MA meter;

const float DP_LOW = -60.0;
const float DP_HIGH = 60.0;

float currentToDewC(float current_mA) {
  return DP_LOW + ((current_mA - 4.0) / 16.0) * (DP_HIGH - DP_LOW);
}

void setup() {
  M5.begin(true, false, true);
  M5.Power.begin();

  Serial.begin(115200);
  delay(500);

  while (!(meter.begin(&Wire, MODULE_4_20MA_ADDR, 21, 22, 100000UL))) {
    Serial.println("No AIN Module!");
    delay(1000);
  }
  Serial.println("AIN module found.");
}

void loop() {
  uint16_t ch1_raw = meter.getCurrentValue(0);
  uint16_t ch2_raw = meter.getCurrentValue(1);

  float current1_mA = ch1_raw / 100.0;
  float current2_mA = ch2_raw / 100.0;

  float dew1_C = currentToDewC(current1_mA);
  float dew2_C = currentToDewC(current2_mA);

  Serial.printf("CH1 raw:%u  %.2f mA  ->  %.2f C\n", ch1_raw, current1_mA, dew1_C);
  Serial.printf("CH2 raw:%u  %.2f mA  ->  %.2f C\n", ch2_raw, current2_mA, dew2_C);
  Serial.println("----");

  delay(500);
}