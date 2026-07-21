import pandas as pd
import math
import os
import platform
from datetime import datetime
import plotly.graph_objects as go

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

timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ====================================================
# COLORS (SWAPPED HERE)
# ====================================================
dew_color = "orange"
pressure_color = "cyan"

# ====================================================
# DEW POINT (TOP)
# ====================================================
fig_dew = go.Figure()

fig_dew.add_trace(go.Scatter(
    x=df["Time"], y=df["DewPoint"],
    mode='lines+markers',
    name="Dew Point",
    line=dict(color=dew_color),
    marker=dict(color=dew_color)
))

fig_dew.update_layout(
    title="Dew Point",
    xaxis_title="Time",
    yaxis_title="Dew Point (°C)",
    template="plotly_dark"
)

# ====================================================
# COMBINED (SECOND)
# ====================================================
fig_comb = go.Figure()

fig_comb.add_trace(go.Scatter(
    x=df["Time"], y=df["DewPoint"],
    name="Dew Point",
    line=dict(color=dew_color)
))

fig_comb.add_trace(go.Scatter(
    x=df["Time"], y=df["SatPressure"],
    name="Pressure",
    yaxis='y2',
    line=dict(color=pressure_color)
))

fig_comb.update_layout(
    title="Combined",
    xaxis_title="Time",
    yaxis=dict(title="Dew Point (°C)"),
    yaxis2=dict(title="Pressure (hPa)", overlaying='y', side='right'),
    template="plotly_dark"
)

# ====================================================
# HTML
# ====================================================
html = f"""
<html>
<head>
<meta charset="UTF-8">
<meta http-equiv="refresh" content="30">
</head>

<body style="background:#111;color:white;text-align:center;">

<h1>🔴 Live Vaisala Dashboard</h1>
<p>{timestamp}</p>

<h2>Dew Point</h2>
{fig_dew.to_html(full_html=False)}

<h2>Combined</h2>
{fig_comb.to_html(full_html=False)}

<p><a href="static.html" style="color:orange;">📊 Go to Static</a></p>

</body>
</html>
"""

with open(os.path.join(save_path, "live.html"), "w", encoding="utf-8") as f:
    f.write(html)

print("\n✅ Live page saved!")
# print("👉 Open AFTER sync:")
# print("https://cisik.web.cern.ch/cisik/HGCAL_MMTT/Vaisala/Test2/live.html")


