import serial
import minimalmodbus
import time
from datetime import datetime
import csv
import threading
import schedule
import os

# ====================================================
# CONFIG
# ====================================================
dateFormat = "%d.%m.%Y, %H:%M:%S"
myPort = '/dev/ttyACM0'
mySlave = 33
zeroKelvin = -273.15

# ✅ SAME PATH AS DASHBOARD
base_path = r"/home/daq/Vaisala_Results_May29"
os.makedirs(base_path, exist_ok=True)

CSVfile = os.path.join(base_path, datetime.now().strftime("VaisalaTest_%d-%m-%Y.csv"))

saveCSV = True

# ====================================================
# SERIAL SETUP
# ====================================================
ser = serial.Serial(myPort, 115200, timeout=1)
myVaisala = minimalmodbus.Instrument(ser, mySlave, minimalmodbus.MODE_RTU, True, False)

# ====================================================
# CSV SAVE
# ====================================================
def storeData(values):
    if not os.path.exists(CSVfile):
        print("Creating", CSVfile)
        with open(CSVfile, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            header = ["Date_Time"]
            for i in range(2):
                header.append(f"ADCcounts{i+1}")
                header.append(f"DewPoint{i+1} [C]")
            writer.writerow(header)

    with open(CSVfile, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        row = [datetime.now().strftime(dateFormat)] + values
        writer.writerow(row)

# ====================================================
# MAIN READ
# ====================================================
def runMain():
    try:
        if not ser.is_open:
            ser.open()

        data = myVaisala.read_registers(0, 4, 4)

        data[1] = data[1]*0.01 + zeroKelvin
        data[3] = data[3]*0.01 + zeroKelvin

        print(datetime.now().strftime(dateFormat), data)

        if saveCSV:
            storeData(data)

    except minimalmodbus.NoResponseError:
        print("No response")

    except Exception as e:
        print("Error:", e)

    finally:
        time.sleep(0.05)
        if ser.is_open:
            ser.close()

# ====================================================
# THREAD WRAPPER
# ====================================================
def run_threaded(job_func):
    threading.Thread(target=job_func).start()

# ====================================================
# SCHEDULE (every 5 sec)
# ====================================================
schedule.every(5).seconds.do(run_threaded, runMain)

print("✅ Vaisala logger running...")

while True:
    schedule.run_pending()
    time.sleep(1)

