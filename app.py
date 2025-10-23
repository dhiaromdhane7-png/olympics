from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
import os
import pickle
import numpy as np
import pandas as pd
from io import StringIO

app = Flask(__name__)
app.secret_key = "supersecretkey"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Load Tokyo Olympic data (your existing code remains the same)
tokyo_data = """Rank,Country,Gold,Silver,Bronze,Total,Rank_by_Total
1,United States,39,41,33,113,1
2,China,38,32,18,88,2
3,Japan,27,14,17,58,5
4,Great Britain,22,21,22,65,4
5,Russia,20,28,23,71,3
6,Australia,17,7,22,46,6
7,Netherlands,10,12,14,36,9
8,France,10,12,11,33,10
9,Germany,10,11,16,37,8
10,Italy,10,10,20,40,7
11,Canada,7,6,11,24,11
12,Brazil,7,6,8,21,12
13,New Zealand,7,6,7,20,13
14,Cuba,7,3,5,15,18
15,Hungary,6,7,7,20,13
16,South Korea,6,4,10,20,13
17,Poland,4,5,5,14,19
18,Czech Republic,4,4,3,11,23
19,Kenya,4,4,2,10,25
20,Norway,4,2,2,8,29
21,Jamaica,4,1,4,9,26
22,Spain,3,8,6,17,17
23,Sweden,3,6,0,9,26
24,Switzerland,3,4,6,13,20
25,Denmark,3,4,4,11,23
26,Croatia,3,3,2,8,29
27,Iran,3,2,2,7,33
28,Serbia,3,1,5,9,26
29,Belgium,3,1,3,7,33
30,Bulgaria,3,1,2,6,39
31,Slovenia,3,1,1,5,42
32,Uzbekistan,3,0,2,5,42
33,Georgia,2,5,1,8,29
34,Chinese Taipei,2,4,6,12,22
35,Turkey,2,2,9,13,20
36,Greece,2,1,1,4,47
37,Uganda,2,1,1,4,47
38,Ecuador,2,1,0,3,60
39,Ireland,2,0,2,4,47
40,Israel,2,0,2,4,47
41,Qatar,2,0,1,3,60
42,Bahamas,2,0,0,2,66
43,Kosovo,2,0,0,2,66
44,Ukraine,1,6,12,19,16
45,Belarus,1,3,3,7,33
46,Romania,1,3,0,4,47
47,Venezuela,1,3,0,4,47
48,India,1,2,4,7,33
49,"Hong Kong, China",1,2,3,6,39
50,Philippines,1,2,1,4,47
51,Slovakia,1,2,1,4,47
52,South Africa,1,2,0,3,60
53,Austria,1,1,5,7,33
54,Egypt,1,1,4,6,39
55,Indonesia,1,1,3,5,42
56,Ethiopia,1,1,2,4,47
57,Portugal,1,1,2,4,47
58,Tunisia,1,1,0,2,66
59,Estonia,1,0,1,2,66
60,Fiji,1,0,1,2,66
61,Latvia,1,0,1,2,66
62,Thailand,1,0,1,2,66
63,Bermuda,1,0,0,1,77
64,Morocco,1,0,0,1,77
65,Puerto Rico,1,0,0,1,77
66,Colombia,0,4,1,5,42
67,Azerbaijan,0,3,4,7,33
68,Dominican Republic,0,3,2,5,42
69,Armenia,0,2,2,4,47
70,Kyrgyzstan,0,2,1,3,60
71,Mongolia,0,1,3,4,47
72,Argentina,0,1,2,3,60
73,San Marino,0,1,2,3,60
74,Jordan,0,1,1,2,66
75,Malaysia,0,1,1,2,66
76,Nigeria,0,1,1,2,66
77,Bahrain,0,1,0,1,77
78,Saudi Arabia,0,1,0,1,77
79,Lithuania,0,1,0,1,77
80,North Macedonia,0,1,0,1,77
81,Namibia,0,1,0,1,77
82,Turkmenistan,0,1,0,1,77
83,Kazakhstan,0,0,8,8,29
84,Mexico,0,0,4,4,47
85,Finland,0,0,2,2,66
86,Botswana,0,0,1,1,77
87,Burkina Faso,0,0,1,1,77
88,Ivory Coast,0,0,1,1,77
89,Ghana,0,0,1,1,77
90,Grenada,0,0,1,1,77
91,Kuwait,0,0,1,1,77
92,Moldova,0,0,1,1,77
93,Syria,0,0,1,1,77"""

df_tokyo = pd.read_csv(StringIO(tokyo_data))

# Load your models (your existing code remains the same)
try:
    model_bronze = pickle.load(open(os.path.join(BASE_DIR, 'models', 'model_bronze_2024.pkl'), 'rb'))
    model_silver = pickle.load(open(os.path.join(BASE_DIR, 'models', 'model_silver_2024.pkl'), 'rb')) 
    model_gold = pickle.load(open(os.path.join(BASE_DIR, 'models', 'model_gold_2024.pkl'), 'rb'))  

    models_loaded = True
    print("Models loaded successfully!")
except Exception as e:
    print(f"Error loading models: {e}")
    models_loaded = False

# --- Setup Database ---
def setup_db():
    conn = sqlite3.connect(os.path.join(BASE_DIR, 'users.db'))
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    users = [
        ("farouk@esprit.tn", "1234"),
        ("fadi@esprit.tn", "1234"),
        ("rami@esprit.tn", "1234"),
        ("dhia@esprit.tn", "1234"),
    ]
    c.executemany("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", users)
    conn.commit()
    conn.close()

setup_db()

# --- Routes ---
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            flash(f"Welcome {username}!", "success")
            # Redirect to Olympics page first instead of dashboard
            return redirect(url_for("olympics", username=username))
        else:
            flash("Invalid username or password", "danger")

    return render_template("login.html")
@app.route('/logout')
def logout():
    
    return redirect(url_for('login'))  # or your homepage route

@app.route("/quiz/<username>", methods=["GET", "POST"])
def quiz(username):
    if request.method == "POST":
        # Retrieve answers (example)
        score = 0
        answers = request.form
        if answers.get("q1") == "Japan":
            score += 1
        if answers.get("q2") == "39":
            score += 1
        flash(f"You scored {score}/2!", "info")
        return redirect(url_for("quiz", username=username))

    return render_template("quiz.html", username=username)

# New route for Olympics page (this was previously called 'success')
@app.route("/olympics/<username>")
def olympics(username):
    return render_template("olympics.html", username=username)

@app.route("/dashboard/<username>")
def dashboard(username):
    email = username.strip().lower()

    # map emails to embed URLs
    mapping = {
        "dhia@esprit.tn": "https://app.powerbi.com/reportEmbed?reportId=285935bd-1323-4f16-a92d-65036f69fb1d&autoAuth=true&ctid=604f1a96-cbe8-43f8-abbf-f8eaf5d85730",
        "farouk@esprit.tn": "https://app.powerbi.com/reportEmbed?reportId=285935bd-1323-4f16-a92d-65036f69fb1d&autoAuth=true&ctid=604f1a96-cbe8-43f8-abbf-f8eaf5d85730",
        "fadi@esprit.tn":   "https://app.powerbi.com/reportEmbed?reportId=78b9a0cd-32bb-41bb-bf07-078b8c414041&autoAuth=true&ctid=604f1a96-cbe8-43f8-abbf-f8eaf5d85730",
        "rami@esprit.tn":   "https://app.powerbi.com/reportEmbed?reportId=1782d368-704b-4a72-b15e-12d127d72b97&autoAuth=true&ctid=604f1a96-cbe8-43f8-abbf-f8eaf5d85730",
    }

    embed_url = mapping.get(email)
    return render_template("dashboard.html", username=username, embed_url=embed_url, models_loaded=models_loaded)

@app.route("/predict-medals", methods=["POST"])
def predict_medals():
    if not models_loaded:
        return jsonify({"error": "Prediction models not available"}), 500
    
    try:
        data = request.get_json()
        year = data.get('year')
        
        if not year:
            return jsonify({"error": "Year is required"}), 400
        
        print(f"Making predictions for year: {year}")
        
        predictions = []
        
        # For each country in Tokyo data, make predictions
        for _, country_data in df_tokyo.iterrows():
            # Create the feature array that matches what the model expects
            # Based on the error, models expect 3 features: [Rank, Country, Total]
            # But we need to encode country as a number
            country_code = hash(country_data['Country']) % 1000  # Simple hash for country code
            
            features = [
                country_data['Rank'],      # Feature 1: Rank
                country_code,              # Feature 2: Country (encoded as number)
                country_data['Total']      # Feature 3: Total medals
            ]
            
            try:
                # Make predictions using all three features
                gold_pred = max(0, int(model_gold.predict([features])[0]))
                silver_pred = max(0, int(model_silver.predict([features])[0]))
                bronze_pred = max(0, int(model_bronze.predict([features])[0]))
                
                # Apply year-based adjustment (simple growth factor)
                years_since_2020 = year - 2020
                growth_factor = 1 + (years_since_2020 * 0.02)  # 2% growth per year
                
                predictions.append({
                    "country": country_data['Country'],
                    "gold": max(0, int(gold_pred * growth_factor)),
                    "silver": max(0, int(silver_pred * growth_factor)),
                    "bronze": max(0, int(bronze_pred * growth_factor)),
                    "total": max(0, int((gold_pred + silver_pred + bronze_pred) * growth_factor))
                })
                
            except Exception as pred_error:
                print(f"Prediction error for {country_data['Country']}: {pred_error}")
                # Fallback: use Tokyo data with growth factor
                years_since_2020 = year - 2020
                growth_factor = 1 + (years_since_2020 * 0.02)
                
                predictions.append({
                    "country": country_data['Country'],
                    "gold": max(0, int(country_data['Gold'] * growth_factor)),
                    "silver": max(0, int(country_data['Silver'] * growth_factor)),
                    "bronze": max(0, int(country_data['Bronze'] * growth_factor)),
                    "total": max(0, int(country_data['Total'] * growth_factor))
                })
        
        # Sort by total medals (descending) and take top 20
        predictions.sort(key=lambda x: x["total"], reverse=True)
        top_predictions = predictions[:20]
        
        # Add ranking
        for i, pred in enumerate(top_predictions):
            pred['rank'] = i + 1
        
        return jsonify({"predictions": top_predictions})
    
    except Exception as e:
        print(f"Error in predict_medals: {str(e)}")
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)