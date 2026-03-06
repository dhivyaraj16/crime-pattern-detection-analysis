from flask import Flask, render_template, request, redirect, url_for, session
from flask import session, redirect
from flask import jsonify
import os
import csv
from datetime import datetime
import re

import json

import pandas as pd

# ================= APP CONFIG ================= #

app = Flask(__name__)
app.secret_key = "crime_prediction_secret_key"

# ================= LOAD DATA ================= #
# ================= DATA LOADER ================= #

DATA_FILE = "data/Crimes_in_india_2001-2013.csv"

def load_data(path=None):
    global df, crime_columns, states

    file_path = path if path else DATA_FILE

    df = pd.read_csv(file_path)

    # Clean columns
    df.columns = df.columns.str.strip()

    # Clean states
    df["STATE/UT"] = df["STATE/UT"].astype(str)
    df["STATE/UT"] = df["STATE/UT"].str.strip()
    df["STATE/UT"] = df["STATE/UT"].str.replace(r"\s*&\s*", " & ", regex=True)
    df["STATE/UT"] = df["STATE/UT"].str.replace(r"\s+", " ", regex=True)
    df["STATE/UT"] = df["STATE/UT"].str.title()

    # Crime columns
    crime_columns = df.columns[3:]

    # States
    states = sorted(df["STATE/UT"].unique())

    print("✅ Dataset Loaded:", file_path)
    print("📅 Years:", df["YEAR"].min(), "-", df["YEAR"].max())


# Load default dataset at startup
load_data()

# ================= LOGIN ================= #


@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if username == "admin" and password == "admin":

            session["user"] = username
            return redirect("/dashboard")

        else:
            return render_template("login.html",
                                   error="Invalid login")

    return render_template("login.html")



@app.route("/update_data")
def update_data():
    os.system("python update_dataset.py")
    return "Dataset updated successfully! 🎉"

# ================= DASHBOARD ================= #

@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/")

    total_states = df["STATE/UT"].nunique()
    total_districts = df["DISTRICT"].nunique()
    total_crime_types = len(crime_columns)

    start_year = df["YEAR"].min()
    end_year = df["YEAR"].max()

    return render_template(
        "dashboard.html",
        total_states=total_states,
        total_districts=total_districts,
        total_crime_types=total_crime_types,
        start_year=start_year,
        end_year=end_year
    )

@app.route("/logout")
def logout():

    session.clear()
    return redirect("/")
# ================= CURRENT PREDICTION ================= #


# ================= CURRENT PREDICTION ================= #

@app.route("/current", methods=["GET", "POST"])
def current():

    if "user" not in session:
        return redirect("/")
    global df

    # Dropdown values
    states = sorted(df["STATE/UT"].dropna().unique())
    crimes = list(df.columns[3:])   # Crime columns

    districts = sorted(df["DISTRICT"].dropna().unique())
    years = sorted(df["YEAR"].dropna().unique())

    if request.method == "POST":

        state = request.form.get("state")
        district = request.form.get("district")
        crime = request.form.get("crime")
        year = int(request.form.get("year"))

        # Filter data
        data = df[
            (df["STATE/UT"] == state) &
            (df["DISTRICT"] == district)
        ].sort_values("YEAR")


        # ---------------- Prediction ---------------- #

        row = data[data["YEAR"] == year]

        if row.empty:
            predicted = 0
        else:
            predicted = int(row[crime].values[0])


        # ---------------- Trend ---------------- #

        trend_years = data["YEAR"].tolist()
        trend_values = data[crime].tolist()

        if len(trend_values) > 1:

            if trend_values[-1] > trend_values[0]:
                trend = "Increasing 📈"

            elif trend_values[-1] < trend_values[0]:
                trend = "Decreasing 📉"

            else:
                trend = "Stable ➖"

        else:
            trend = "No Data"


        # ---------------- Anomaly Detection ---------------- #

        mean = data[crime].mean()
        std = data[crime].std()

        if predicted > mean + std:
            anomaly = "High Spike ⚠️"

        elif predicted < mean - std:
            anomaly = "Sudden Drop ⚠️"

        else:
            anomaly = "Normal ✅"


        # ---------------- Hotspot Detection ---------------- #

        state_data = df[df["STATE/UT"] == state]

        state_total = state_data[crime].sum()
        avg_total = df.groupby("STATE/UT")[crime].sum().mean()

        if state_total > avg_total:
            hotspot = "Yes 🔴 (High Crime Area)"
        else:
            hotspot = "No 🟢 (Normal Area)"


        # ---------------- Risk Level ---------------- #

        if predicted >= 500:
            risk = "High 🔴"

        elif predicted >= 200:
            risk = "Medium 🟠"

        else:
            risk = "Low 🟢"


        # ---------------- Prevention ---------------- #

        if risk == "High 🔴":

            prevention = [
                "Install more CCTV cameras",
                "Increase night patrol",
                "Public awareness programs",
                "Emergency helpline monitoring",
                "Strict law enforcement"
            ]

            patrol = "24x7 Intensive Patrol 🚔"
            police_deployment = "Special crime units, rapid response teams, and continuous monitoring"

            safety_advice = "Avoid isolated areas, stay alert, use emergency contacts, and report suspicious activities"

        elif risk == "Medium 🟠":

            prevention = [
                "Regular police monitoring",
                "Community awareness",
                "Improve street lighting",
                "Periodic checking"
            
            ]
            patrol = "Daily Patrol 🚓"
            police_deployment = "Regular patrolling teams and area monitoring units"

            safety_advice = "Be cautious in public places, avoid late-night travel alone, stay connected"


        else:

            prevention = [
                "Maintain security",
                "Citizen awareness",
                "Continue surveillance"
            ]

            patrol = "Routine Patrol 👮"
            
            police_deployment = "Normal duty officers and routine monitoring"

            safety_advice = "Follow basic safety rules and cooperate with authorities"


        # ---------------- Severity ---------------- #

        if predicted < 100:
            severity = "Low 🟢"

        elif predicted < 300:
            severity = "Medium 🟠"

        else:
            severity = "High 🔴"


        return render_template(
            "current.html",

            states=states,
            districts=districts,
            crimes=crimes,
            years=years,

            state=state,
            district=district,
            crime=crime,
            year=year,

            predicted_count=predicted,
            severity=severity,

            trend=trend,
            anomaly=anomaly,
            hotspot=hotspot,
            risk=risk,
            patrol=patrol,
            prevention=prevention,
            police_deployment=police_deployment,
            safety_advice=safety_advice,

            trend_years=trend_years,
            trend_values=trend_values
        )


    return render_template(
        "current.html",
        states=states,
        districts=districts,
        crimes=crimes,
        years=years
    )


# ================= DISTRICT API ================= #

@app.route("/get_states")
def get_states():
    return jsonify(sorted(df["STATE/UT"].unique().tolist()))




@app.route("/get_crimes")
def get_crimes():
    return jsonify(sorted(crime_columns))





# ================= FUTURE PREDICTION ================= #

@app.route("/future", methods=["GET", "POST"])
def future():

    if "user" not in session:
        return redirect("/")
    global df

    states = sorted(df["STATE/UT"].dropna().unique())
    crimes = list(crime_columns)
    districts=sorted(df["DISTRICT"].dropna().unique())
    max_year = int(df["YEAR"].max())
    years = list(range(max_year + 1, max_year + 14))
    if request.method == "POST":

        # Get form values
        state = request.form.get("state")
        district = request.form.get("district")
        crime = request.form.get("crime")
        year = int(request.form.get("year"))

        # Filter history
        history = df[
            (df["STATE/UT"] == state) &
            (df["DISTRICT"] == district)
        ].sort_values("YEAR")

        # ---------------- Prediction ----------------

        if len(history) < 2:

            predicted = int(history[crime].mean()) if not history.empty else 0
            trend = "Stable ➖"

        else:

            last = history[crime].iloc[-1]
            prev = history[crime].iloc[-2]

            predicted = int(last + (last - prev))

            if predicted > last:
                trend = "Increasing 📈"
            elif predicted < last:
                trend = "Decreasing 📉"
            else:
                trend = "Stable ➖"

        if predicted < 0:
            predicted = 0


        # ---------------- Risk % ----------------

        max_val = history[crime].max() if not history.empty else 1

        if max_val == 0:
            risk_percent = 0
        else:
            risk_percent = int((predicted / max_val) * 100)


        if risk_percent > 70:
            risk = "High Risk 🔴"
        elif risk_percent > 40:
            risk = "Medium Risk 🟠"
        else:
            risk = "Low Risk 🟢"


        # ---------------- Top 5 Crimes (Location) ----------------

        top_data = history[crime_columns].sum().sort_values(ascending=False)

        top_crimes = top_data.head(5).index.tolist()


        # ---------------- Public Prevention ----------------

        public = [
            "Avoid isolated places at night",
            "Use street lights",
            "Report suspicious activity",
            "Install safety locks",
            "Join community groups"
        ]


        # ---------------- Police Prevention ----------------

        police = [
            "Night patrolling",
            "CCTV monitoring",
            "Quick response teams",
            "Awareness campaigns",
            "Data-based surveillance"
        ]


        # ---------------- Deployment Plan ----------------

        if "High" in risk:

            deployment = {
                "Patrol": "24x7 Intensive Patrol",
                "CCTV": "High Surveillance",
                "Prevention": "Community + Night Checks",
                "Response": "Rapid Action Team"
            }

        elif "Medium" in risk:

            deployment = {
                "Patrol": "Regular Patrol",
                "CCTV": "Medium Surveillance",
                "Prevention": "Public Awareness",
                "Response": "Quick Response Unit"
            }

        else:

            deployment = {
                "Patrol": "Normal Patrol",
                "CCTV": "Basic Monitoring",
                "Prevention": "Routine Checks",
                "Response": "Local Police Support"
            }


        # ---------------- Send Data to HTML ----------------

        return render_template(
            "future.html",

            states=states,
            districts=districts,
            crimes=crimes,
            years=years,

            state=state,
            district=district,
            crime=crime,
            year=year,

            predicted=predicted,
            risk_percent=risk_percent,
            risk=risk,
            trend=trend,

            top_crimes=top_crimes,
            public=public,
            police=police,

            deployment=deployment
        )


    # First page load (GET)

    return render_template(
        "future.html",
        states=states,
        districts=districts,
        crimes=crimes,
        years=years
    )


# ================= ANALYSIS ================= #
@app.route("/analysis")
def analysis():

    if "user" not in session:
        return redirect("/")

    state = request.args.get("state","All")
    district = request.args.get("district","All")

    data = df.copy()

    if state != "All":
        data = data[data["STATE/UT"] == state]

    if district != "All":
        data = data[data["DISTRICT"] == district]


    # Total Crimes
    total = int(data["TOTAL IPC CRIMES"].sum())


    # Crime Sum
    crime_sum = data[crime_columns].sum()


    # Top 5
    top = crime_sum.sort_values(ascending=False).head(5)

    # Bottom 5
    bottom = crime_sum.sort_values().head(5)


    # Year Trend
    year_sum = data.groupby("YEAR")["TOTAL IPC CRIMES"].sum()


    # States
    states = sorted(df["STATE/UT"].unique())


    return render_template(

        "analysis.html",

        total=total,

        topLabels=json.dumps(top.index.tolist()),
        topValues=json.dumps(top.values.astype(int).tolist()),

        bottomLabels=json.dumps(bottom.index.tolist()),
        bottomValues=json.dumps(bottom.values.astype(int).tolist()),

        years=json.dumps(year_sum.index.astype(str).tolist()),
        yearValues=json.dumps(year_sum.values.astype(int).tolist()),

        states=states,

        selected_state=state,
        selected_district=district
    )


# ================= API =================

@app.route("/get_districts/<state>")
def get_districts(state):

    districts = df[df["STATE/UT"] == state]["DISTRICT"].unique().tolist()

    districts.sort()

    return jsonify(districts)


    # -------- Detect Total Column --------
    

# ================= RESULTS ================= #
@app.route("/predict", methods=["POST"])
def predict():

    year = request.form["year"]

   
    # Save history
    history_file = "prediction_history.csv"

    file_exists = os.path.isfile(history_file)

    with open(history_file, "a", newline="") as file:
        writer = csv.writer(file)

        # Write header first time
        if not file_exists:
            writer.writerow(["DateTime", "Year", "Prediction"])

        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            year,
            prediction
        ])

    return redirect("/history")

@app.route("/history")
def history():

    history_file = "prediction_history.csv"

    data = []

    if os.path.exists(history_file):

        with open(history_file, "r") as file:
            reader = csv.reader(file)
            next(reader)  # skip header

            for row in reader:
                data.append(row)

    return render_template("history.html", data=data)

@app.route("/results")
def results():

    if "user" not in session:
        return redirect("/")

    return render_template("results.html")

@app.route("/trend", methods=["POST"])
def trend():

    global df

    state = request.form.get("state")
    district = request.form.get("district")
    crime = request.form.get("crime")

  

    # Filter data
    data = df[
        (df["STATE/UT"] == state) &
        (df["DISTRICT"] == district)
    ].sort_values("YEAR")

    years = data["YEAR"].tolist()
    values = data[crime].tolist()


    return render_template(
        "analysis.html",
        years=years,
        values=values,
        state=state,
        district=district,
        crime=crime
    )

import os
from flask import request, redirect, render_template

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)



@app.route("/upload", methods=["GET", "POST"])
def upload():

    if "user" not in session:
        return redirect("/")

    if request.method == "POST":

        file = request.files.get("file")

        if not file:
            return "No file selected"

        if not file.filename.endswith(".csv"):
            return "Only CSV files allowed"

        filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)

        file.save(filepath)

        # Reload using loader
        load_data(filepath)

        print("✅ New Dataset Applied")

        return redirect("/dashboard")

    return render_template("upload.html")


# ================= RUN ================= #

if __name__ == "__main__":

    app.run(debug=True)

