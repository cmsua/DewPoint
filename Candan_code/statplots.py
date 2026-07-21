import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import math
import os
import platform
import time

# ====================================================
# PATH
# ====================================================
system = platform.system()

if system == "Windows":
    save_path = r"C:\Users\cisik\CERNBox\www\HGCAL_MMTT\Vaisala\Test2"
elif system == "Darwin":
    save_path = "/Users/candanisik/eos/www/HGCAL_MMTT/Vaisala/Test"
else:
     save_path = os.path.join(os.getcwd()+'/Vaisala_Results', "output")
os.makedirs(save_path, exist_ok=True)

print("Saving to:", save_path)

# ====================================================
# LOAD CSV
# ====================================================
csv_path=os.getcwd()+'/Vaisala_Results'
csv_files = [f for f in os.listdir(csv_path) if f.endswith(".csv")]
csv_file = max(csv_files, key=lambda x: os.path.getmtime(csv_path+'/'+x))

print("Using CSV:", csv_path+'/'+csv_file)

df = pd.read_csv(csv_path+'/'+csv_file)

dew_col = [c for c in df.columns if "dew" in c.lower()][0]
time_col = [c for c in df.columns if "date" in c.lower()][0]

df["DewPoint"] = pd.to_numeric(df[dew_col], errors='coerce')
df["Time"] = pd.to_datetime(df[time_col], format="%d.%m.%Y, %H:%M:%S", errors='coerce')



df = df.dropna().sort_values("Time")

print(df)
# ====================================================
# GOFF-GRATCH
# ====================================================
def goff_gratch_svp(temp_c):
    T = temp_c + 273.15
    return 10**(
        -7.90298 * ((373.16 / T) - 1)
        + 5.02808 * math.log10(373.16 / T)
        - 1.3816e-7 * (10**(11.344 * (1 - T/373.16)) - 1)
        + 8.1328e-3 * (10**(-3.49149 * (373.16/T - 1)) - 1)
        + math.log10(1013.246)
    )

df["SatPressure"] = df["DewPoint"].apply(goff_gratch_svp)

# ====================================================
# STYLE
# ====================================================
plt.style.use("dark_background")

def style(ax):
    ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

# ====================================================
# COLORS (SWAPPED HERE)
# ====================================================
dew_color = "orange"
pressure_color = "cyan"

# ====================================================
# DEW POINT
# ====================================================
fig1, ax1 = plt.subplots(figsize=(12,6))
ax1.plot(df["Time"], df["DewPoint"], color=dew_color)
ax1.set_title("Dew Point vs Time")
ax1.set_xlabel("Time")
ax1.set_ylabel("Dew Point (°C)")
style(ax1)

plt.xticks(rotation=45)
plt.tight_layout()
fig1.savefig(os.path.join(save_path, "dewpoint_plot.png"), dpi=300)

# ====================================================
# PRESSURE
# ====================================================
fig2, ax2 = plt.subplots(figsize=(12,6))
ax2.plot(df["Time"], df["SatPressure"], color=pressure_color)
ax2.set_title("Pressure vs Time")
ax2.set_xlabel("Time")
ax2.set_ylabel("Pressure (hPa)")
style(ax2)

plt.xticks(rotation=45)
plt.tight_layout()
fig2.savefig(os.path.join(save_path, "pressure_plot.png"), dpi=300)

# ====================================================
# STATIC HTML
# ====================================================
html = """
<html>
<head>
<meta charset="UTF-8">
</head>

<body style="background:black;color:white;text-align:center;">

<h1>📊 Static Vaisala Plots</h1>

<h2>Dew Point</h2>
<img src="dewpoint_plot.png" width="80%"><br><br>

<h2>Pressure</h2>
<img src="pressure_plot.png" width="80%"><br><br>

<p><a href="live.html" style="color:cyan;">🔴 Go to Live Dashboard</a></p>

</body>
</html>
"""

with open(os.path.join(save_path, "static.html"), "w", encoding="utf-8") as f:
    f.write(html)

# ====================================================
# WAIT FOR CERNBOX SYNC
# ====================================================
#print("\n⏳ Waiting for CERNBox sync...")
#time.sleep(10)

# ====================================================
# PRINT LINKS
# ====================================================
print("\n✅ Static dashboard ready!")

#print("🌐 STATIC PAGE:")
#print("https://cisik.web.cern.ch/cisik/HGCAL_MMTT/Vaisala/Test2/static.html")

#print("\n📊 DIRECT IMAGES:")
#print("https://cisik.web.cern.ch/cisik/HGCAL_MMTT/Vaisala/Test2/dewpoint_plot.png")
#print("https://cisik.web.cern.ch/cisik/HGCAL_MMTT/Vaisala/Test2/pressure_plot.png")
