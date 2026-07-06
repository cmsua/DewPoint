Here is a small `README.md` you can put in the project folder.

````markdown
# M5Stack Vaisala Dew Point Logger

This project reads two Vaisala DMT242 dew point sensors using an M5Stack and a 4–20 mA AIN module.

The M5Stack reads both analog current signals, converts them to dew point, and acts as a Modbus RTU slave over USB serial. A Windows Python logger reads the M5 over Modbus and saves the data to a CSV file. A local Flask dashboard reads that CSV and plots the live data.

---

## System Overview

```text
Vaisala Sensor 1 ─┐
                  ├─> M5Stack AIN 4–20 mA Module ─> M5Stack Arduino Program
Vaisala Sensor 2 ─┘                                      │
                                                         │ USB Serial / Modbus RTU
                                                         ↓
                                                  Windows Python Logger
                                                         │
                                                         ↓
                                                    CSV File
                                                         │
                                                         ↓
                                                 Localhost Dashboard
````

---

## Hardware Used

* M5Stack Core / Fire
* M5Stack AIN 4–20 mA module
* Two Vaisala DMT242 dew point transmitters
* External power supply for the Vaisala sensors
* Windows PC with USB connection to the M5Stack

---

## Sensor Scaling

For the Vaisala DMT242B range:

```text
4 mA  = -60 °C dew point
20 mA = +60 °C dew point
```

The M5 program converts current to dew point using:

```text
dew_C = -60 + ((current_mA - 4) / 16) * 120
```

---

# Arduino IDE Setup for M5Stack

## 1. Install Arduino IDE

Download and install Arduino IDE 2.x:

```text
https://www.arduino.cc/en/software
```

---

## 2. Add the M5Stack Board Manager URL

Open Arduino IDE.

Go to:

```text
File → Preferences
```

Find:

```text
Additional boards manager URLs
```

Add:

```text
https://static-cdn.m5stack.com/resource/arduino/package_m5stack_index.json
```

Click OK.

---

## 3. Install the M5Stack Board Package

Go to:

```text
Tools → Board → Boards Manager
```

Search:

```text
M5Stack
```

Install the M5Stack board package.

If you get compile errors involving:

```text
rom/miniz.h
```

then use M5Stack board package version:

```text
2.1.4
```

That version worked for this project.

---

## 4. Select the Correct Board

Go to:

```text
Tools → Board
```

Select the board matching your device.

For our setup, we used:

```text
M5Stack-FIRE
```

If using a different M5Stack model, select the matching board.

---

## 5. Select the COM Port

Plug in the M5Stack over USB.

Go to:

```text
Tools → Port
```

Select the COM port for the M5Stack.

Example:

```text
COM4
```

This same COM port must later be used in `logger.py`.

---

## 6. Install Required Arduino Libraries

Go to:

```text
Sketch → Include Library → Manage Libraries
```

Install:

```text
M5Stack
M5GFX
M5Unified
```

---

## 7. Install the 4–20 mA Module Library

The 4–20 mA library may not appear in Arduino Library Manager.

Download it manually from GitHub:

```text
https://github.com/m5stack/M5Module-4-20mA
```

Click:

```text
Code → Download ZIP
```

Then in Arduino IDE:

```text
Sketch → Include Library → Add .ZIP Library
```

Select the downloaded ZIP file.

The library should provide:

```cpp
#include "MODULE_4_20MA.h"
```

---

## 8. Upload the M5 Program

Open:

```text
m5_vaisala_modbus.ino
```

Click Upload.

The M5 screen should show:

```text
M5 Modbus Slave
CH1: xx.xx mA
CH2: xx.xx mA
D1: xx.xx C
D2: xx.xx C
```

Important:

After uploading, close the Arduino Serial Monitor before running the Python logger.

Only one program can use the COM port at a time.

---

# Python Setup

## 1. Install Python

Install Python from:

```text
https://www.python.org/downloads/
```

During install, allow Python to be added to PATH if prompted.

Check Python from PowerShell:

```powershell
py --version
```

---

## 2. Install Python Packages

Open PowerShell in the project folder.

Run:

```powershell
py -m pip install minimalmodbus pyserial schedule flask pandas
```

---

# Running the Project

## Step 1: Upload the M5 Arduino Program

Upload:

```text
m5_vaisala_modbus.ino
```

Then close Arduino Serial Monitor.

---

## Step 2: Run the Logger

In PowerShell:

```powershell
py .\logger.py
```

Expected output:

```text
07.05.2026, 13:36:25 I read 1364, 12.30, 1358, 11.85
Data saved to VaisalaTest_07-05-2026.csv
```

This creates a CSV like:

```text
VaisalaTest_07-05-2026.csv
```

CSV columns:

```text
Date_Time
ADCcounts1
DewPoint1 [C]
ADCcounts2
DewPoint2 [C]
```

Note: `ADCcounts` is actually the raw centi-mA current value from the AIN module.

Example:

```text
1364 = 13.64 mA
```

---

## Step 3: Run the Dashboard

Open a second PowerShell window in the same folder.

Run:

```powershell
py .\dashboard.py
```

Then open:

```text
http://127.0.0.1:5000
```

The dashboard reads the newest `VaisalaTest_*.csv` file and plots both sensors.

---

# Modbus Register Map

The M5Stack acts as Modbus slave ID:

```text
33
```

The Python logger reads 4 input registers:

```python
myVaisala.read_registers(0, 4, 4)
```

Register layout:

```text
Register 0 = Sensor 1 current raw value, centi-mA
Register 1 = Sensor 1 dew point, Kelvin × 100
Register 2 = Sensor 2 current raw value, centi-mA
Register 3 = Sensor 2 dew point, Kelvin × 100
```

Example:

```text
[1364, 28545, 1358, 28500]
```

Means:

```text
Sensor 1 current = 13.64 mA
Sensor 1 dew point = 285.45 K - 273.15 = 12.30 °C

Sensor 2 current = 13.58 mA
Sensor 2 dew point = 285.00 K - 273.15 = 11.85 °C
```

---

# Troubleshooting

## `COM4 access denied`

Close:

```text
Arduino Serial Monitor
Arduino Serial Plotter
Other Python scripts using the port
UIFlow
```

Then unplug and replug the M5.

---

## `No response`

Check:

```text
1. M5 is plugged in
2. Correct COM port in logger.py
3. M5 Arduino program is uploaded
4. Arduino Serial Monitor is closed
5. Slave ID is 33
```

---

## Arduino compile error: `M5Stack.h not found`

Install the M5Stack library:

```text
Sketch → Include Library → Manage Libraries → M5Stack
```

---

## Arduino compile error: `MODULE_4_20MA.h not found`

Install the 4–20 mA module library manually:

```text
https://github.com/m5stack/M5Module-4-20mA
```

Then:

```text
Sketch → Include Library → Add .ZIP Library
```

---

## Arduino compile error: `rom/miniz.h`

Use M5Stack board package version:

```text
2.1.4
```

in Boards Manager.

---

# File List

```text
m5_vaisala_modbus.ino   Arduino program for the M5Stack
logger.py               Python Modbus CSV logger
dashboard.py            Localhost live plotting dashboard
README.md               This file
```

```
```
