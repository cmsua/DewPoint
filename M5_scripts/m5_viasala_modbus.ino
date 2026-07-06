#include <M5Stack.h>
#include "MODULE_4_20MA.h"
#include <M5GFX.h>

M5GFX display;
M5Canvas canvas(&display);
MODULE_4_20MA meter;

// -----------------------------
// Modbus settings
// -----------------------------
const uint8_t SLAVE_ID = 33;

// -----------------------------
// Vaisala DMT242B scaling
// 4 mA  = -60 C
// 20 mA = +60 C
// -----------------------------
const float DP_LOW = -60.0;
const float DP_HIGH = 60.0;

// Registers expected by the Python logger:
// reg0 = Sensor 1 raw current value
// reg1 = Sensor 1 dew point in Kelvin x100
// reg2 = Sensor 2 raw current value
// reg3 = Sensor 2 dew point in Kelvin x100
uint16_t regs[4] = {0, 0, 0, 0};


// -----------------------------
// Modbus CRC-16
// -----------------------------
uint16_t modbusCRC(uint8_t *data, int len) {
  uint16_t crc = 0xFFFF;

  for (int pos = 0; pos < len; pos++) {
    crc ^= (uint16_t)data[pos];

    for (int i = 0; i < 8; i++) {
      if (crc & 0x0001) {
        crc >>= 1;
        crc ^= 0xA001;
      } else {
        crc >>= 1;
      }
    }
  }

  return crc;
}


// -----------------------------
// Convert current to dew point
// -----------------------------
float currentToDewC(float current_mA) {
  return DP_LOW + ((current_mA - 4.0) / 16.0) * (DP_HIGH - DP_LOW);
}


// -----------------------------
// Read both AIN channels and update Modbus registers
// -----------------------------
void updateRegisters() {
  // Library returns centi-mA:
  // 1364 means 13.64 mA
  uint16_t ch1_raw = meter.getCurrentValue(0);
  uint16_t ch2_raw = meter.getCurrentValue(1);

  float current1_mA = ch1_raw / 100.0;
  float current2_mA = ch2_raw / 100.0;

  float dew1_C = currentToDewC(current1_mA);
  float dew2_C = currentToDewC(current2_mA);

  float dew1_K = dew1_C + 273.15;
  float dew2_K = dew2_C + 273.15;

  uint16_t dew1_K_x100 = (uint16_t)(dew1_K * 100.0);
  uint16_t dew2_K_x100 = (uint16_t)(dew2_K * 100.0);

  regs[0] = ch1_raw;
  regs[1] = dew1_K_x100;
  regs[2] = ch2_raw;
  regs[3] = dew2_K_x100;

  canvas.clear(BLACK);
  canvas.setCursor(10, 10);
  canvas.setTextSize(2);

  canvas.setTextColor(YELLOW);
  canvas.printf("M5 Modbus Slave\n");

  canvas.setTextColor(GREEN);
  canvas.printf("CH1: %.2f mA\n", current1_mA);
  canvas.printf("CH2: %.2f mA\n", current2_mA);

  canvas.setTextColor(CYAN);
  canvas.printf("D1: %.2f C\n", dew1_C);
  canvas.printf("D2: %.2f C\n", dew2_C);

  canvas.setTextColor(WHITE);
  canvas.printf("R0:%u R1:%u\n", regs[0], regs[1]);
  canvas.printf("R2:%u R3:%u\n", regs[2], regs[3]);
  canvas.printf("Slave:%d F03/F04\n", SLAVE_ID);

  canvas.pushSprite(0, 0);
}


// -----------------------------
// Send Modbus exception response
// -----------------------------
void sendException(uint8_t functionCode, uint8_t exceptionCode) {
  uint8_t response[5];

  response[0] = SLAVE_ID;
  response[1] = functionCode | 0x80;
  response[2] = exceptionCode;

  uint16_t crc = modbusCRC(response, 3);
  response[3] = crc & 0xFF;
  response[4] = (crc >> 8) & 0xFF;

  Serial.write(response, 5);
}


// -----------------------------
// Send Modbus register response
// -----------------------------
void sendRegisterResponse(uint8_t functionCode, uint16_t startReg, uint16_t quantity) {
  uint8_t response[13]; 
  int idx = 0;

  response[idx++] = SLAVE_ID;
  response[idx++] = functionCode;
  response[idx++] = quantity * 2;

  for (int i = 0; i < quantity; i++) {
    uint16_t value = regs[startReg + i];
    response[idx++] = (value >> 8) & 0xFF;
    response[idx++] = value & 0xFF;
  }

  uint16_t crc = modbusCRC(response, idx);
  response[idx++] = crc & 0xFF;
  response[idx++] = (crc >> 8) & 0xFF;

  Serial.write(response, idx);
}


// -----------------------------
// Handle incoming Modbus request
// -----------------------------
void handleModbusRequest(uint8_t *request, int len) {
  if (len < 8) return;

  uint8_t slave = request[0];
  uint8_t functionCode = request[1];

  if (slave != SLAVE_ID) {
    return;
  }

  uint16_t receivedCRC = request[6] | (request[7] << 8);
  uint16_t calculatedCRC = modbusCRC(request, 6);

  if (receivedCRC != calculatedCRC) {
    return;
  }

  // Support both:
  // 0x03 = Read Holding Registers
  // 0x04 = Read Input Registers
  if (functionCode != 0x03 && functionCode != 0x04) {
    sendException(functionCode, 0x01);
    return;
  }

  uint16_t startReg = (request[2] << 8) | request[3];
  uint16_t quantity = (request[4] << 8) | request[5];

  if (quantity == 0 || startReg + quantity > 4) {
    sendException(functionCode, 0x02);
    return;
  }

  updateRegisters();
  sendRegisterResponse(functionCode, startReg, quantity);
}


// -----------------------------
// Setup
// -----------------------------
void setup() {
  M5.begin(true, false, true);
  M5.Power.begin();

  // USB serial used for Modbus RTU
  Serial.begin(115200);

  display.begin();
  canvas.setColorDepth(8);
  canvas.setFont(&fonts::efontCN_12);
  canvas.createSprite(display.width(), display.height());

  canvas.clear(BLACK);
  canvas.setCursor(10, 10);
  canvas.setTextColor(WHITE);
  canvas.setTextSize(2);
  canvas.println("Starting AIN...");
  canvas.pushSprite(0, 0);

  // AIN module on Port A:
  // SDA = 21, SCL = 22, I2C speed = 100 kHz
  while (!(meter.begin(&Wire, MODULE_4_20MA_ADDR, 21, 22, 100000UL))) {
    canvas.clear(BLACK);
    canvas.setCursor(10, 10);
    canvas.setTextColor(RED);
    canvas.setTextSize(2);
    canvas.println("No AIN Module!");
    canvas.pushSprite(0, 0);
    delay(1000);
  }

  updateRegisters();
}


// -----------------------------
// Main loop
// -----------------------------
void loop() {
  updateRegisters();

  if (Serial.available() >= 8) {
    uint8_t request[8];

    for (int i = 0; i < 8; i++) {
      request[i] = Serial.read();
    }

    handleModbusRequest(request, 8);
  }

  delay(100);
}
