import minimalmodbus
import time
from datetime import datetime
import csv
import os
import schedule

dateFormat = "%d.%m.%Y, %H:%M:%S"

myPort = "COM4"   # Change this if Windows gives the M5 a different COM port
mySlave = 33
zeroKelvin = -273.15

CSVfile = datetime.now().strftime("VaisalaTest_%d-%m-%Y.csv")
saveCSV = True

# -----------------------------
# Modbus setup
# -----------------------------
myVaisala = minimalmodbus.Instrument(myPort, mySlave)
myVaisala.serial.baudrate = 115200
myVaisala.serial.timeout = 1
myVaisala.mode = minimalmodbus.MODE_RTU
myVaisala.clear_buffers_before_each_transaction = True


def create_csv_if_needed():
    if not os.path.exists(CSVfile):
        print("Creating", CSVfile)

        with open(CSVfile, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                "Date_Time",
                "ADCcounts1",
                "DewPoint1 [C]",
                "ADCcounts2",
                "DewPoint2 [C]"
            ])


def storeData(values):
    create_csv_if_needed()

    with open(CSVfile, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)

        row = [datetime.now().strftime(dateFormat)]

        for value in values:
            row.append(value)

        writer.writerow(row)

    print("Data saved to", CSVfile)


def runMain():
    try:
        # Read 4 input registers using function code 4
        myData = myVaisala.read_registers(0, 4, 4)

        # Register 1 and 3 are Kelvin x100.
        # Convert to Celsius.
        myData[1] = myData[1] * 0.01 + zeroKelvin
        myData[3] = myData[3] * 0.01 + zeroKelvin

        print(
            "{:s} I read {:d}, {:.2f}, {:d}, {:.2f}".format(
                datetime.now().strftime(dateFormat),
                myData[0],
                myData[1],
                myData[2],
                myData[3]
            )
        )

        if saveCSV:
            storeData(myData)

    except minimalmodbus.NoResponseError:
        print("No response")

    except Exception as e:
        print("Error:", e)


# Run once immediately
runMain()

# Log every 5 seconds
schedule.every().minute.at(":00").do(runMain)
schedule.every().minute.at(":05").do(runMain)
schedule.every().minute.at(":10").do(runMain)
schedule.every().minute.at(":15").do(runMain)
schedule.every().minute.at(":20").do(runMain)
schedule.every().minute.at(":25").do(runMain)
schedule.every().minute.at(":30").do(runMain)
schedule.every().minute.at(":35").do(runMain)
schedule.every().minute.at(":40").do(runMain)
schedule.every().minute.at(":45").do(runMain)
schedule.every().minute.at(":50").do(runMain)
schedule.every().minute.at(":55").do(runMain)

print("Logger running. Press Ctrl+C to stop.")

while True:
    schedule.run_pending()
    time.sleep(1)
