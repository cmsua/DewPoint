from flask import Flask, jsonify, render_template_string
import pandas as pd
import glob
import os

app = Flask(__name__)

CSV_PATTERN = "VaisalaTest_*.csv"

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Vaisala Live Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
    <style>
        body {
            background: #111;
            color: white;
            font-family: Arial, sans-serif;
            text-align: center;
        }
        .box {
            margin: 20px auto;
            width: 90%;
            max-width: 1000px;
            background: #1b1b1b;
            padding: 20px;
            border-radius: 12px;
        }
        .value {
            font-size: 28px;
            margin: 10px;
        }
    </style>
</head>
<body>
    <h1>Vaisala Dew Point Dashboard</h1>
    <p id="lastUpdate">Waiting for data...</p>

    <div class="box">
        <div class="value" id="sensor1">Sensor 1: -- °C</div>
        <div class="value" id="sensor2">Sensor 2: -- °C</div>
    </div>

    <div class="box">
        <div id="plot" style="height:600px;"></div>
    </div>

<script>
async function updateDashboard() {
    const response = await fetch("/data");
    const data = await response.json();

    if (data.error) {
        document.getElementById("lastUpdate").innerText = data.error;
        return;
    }

    document.getElementById("lastUpdate").innerText =
        "Last update: " + data.last_time;

    document.getElementById("sensor1").innerText =
        "Sensor 1: " + data.latest_dew1.toFixed(2) + " °C";

    document.getElementById("sensor2").innerText =
        "Sensor 2: " + data.latest_dew2.toFixed(2) + " °C";

    const trace1 = {
        x: data.times,
        y: data.dew1,
        mode: "lines+markers",
        name: "Sensor 1 Dew Point"
    };

    const trace2 = {
        x: data.times,
        y: data.dew2,
        mode: "lines+markers",
        name: "Sensor 2 Dew Point"
    };

    const layout = {
        title: "Dew Point vs Time",
        paper_bgcolor: "#111",
        plot_bgcolor: "#111",
        font: { color: "white" },
        xaxis: { title: "Time" },
        yaxis: { title: "Dew Point [°C]" }
    };

    Plotly.newPlot("plot", [trace1, trace2], layout);
}

updateDashboard();
setInterval(updateDashboard, 5000);
</script>

</body>
</html>
"""


def get_latest_csv():
    files = glob.glob(CSV_PATTERN)
    if not files:
        return None
    return max(files, key=os.path.getmtime)


@app.route("/")
def index():
    return render_template_string(HTML)


@app.route("/data")
def data():
    csv_file = get_latest_csv()

    if csv_file is None:
        return jsonify({"error": "No VaisalaTest CSV file found yet."})

    try:
        df = pd.read_csv(csv_file)

        df["Time"] = pd.to_datetime(
            df["Date_Time"],
            format="%d.%m.%Y, %H:%M:%S",
            errors="coerce"
        )

        df["DewPoint1 [C]"] = pd.to_numeric(df["DewPoint1 [C]"], errors="coerce")
        df["DewPoint2 [C]"] = pd.to_numeric(df["DewPoint2 [C]"], errors="coerce")

        df = df.dropna().sort_values("Time")

        if df.empty:
            return jsonify({"error": "CSV exists, but no valid data yet."})

        # Keep last 300 points so the browser does not get overloaded
        df = df.tail(300)

        latest = df.iloc[-1]

        return jsonify({
            "csv_file": csv_file,
            "times": df["Time"].dt.strftime("%H:%M:%S").tolist(),
            "dew1": df["DewPoint1 [C]"].tolist(),
            "dew2": df["DewPoint2 [C]"].tolist(),
            "latest_dew1": float(latest["DewPoint1 [C]"]),
            "latest_dew2": float(latest["DewPoint2 [C]"]),
            "last_time": latest["Time"].strftime("%d.%m.%Y %H:%M:%S")
        })

    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == "__main__":
    print("Dashboard running at:")
    print("http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False)
