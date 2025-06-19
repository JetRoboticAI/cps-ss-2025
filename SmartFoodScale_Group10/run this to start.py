from flask import Flask, request, jsonify, render_template_string
import sqlite3
import time
import os

app = Flask(__name__)

# In-memory cache of the latest data
current_weight = None
last_update_time = None

# Database setup
DB_NAME = "record.db"

def init_db():
    if not os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('''CREATE TABLE weights (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        weight REAL,
                        timestamp TEXT
                    )''')
        conn.commit()
        conn.close()

def insert_record(weight, timestamp):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO weights (weight, timestamp) VALUES (?, ?)", (weight, timestamp))
    conn.commit()
    conn.close()

# Serve webpage
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Weight Display</title>
  <style>
    body { font-family: Arial; text-align: center; background: #f5f7fa; padding: 50px; }
    h1 { font-size: 2.5em; margin-bottom: 20px; color: #333; }
    .value { font-size: 4em; font-weight: bold; color: #007bff; margin-top: 30px; }
    .timestamp { color: #888; margin-top: 10px; }
  </style>
</head>
<body>
  <h1>Current Weight (g)</h1>
  <div class="value" id="weight">--</div>
  <div class="timestamp" id="time">Waiting for data...</div>

  <script src="https://code.jquery.com/jquery-3.6.4.min.js"></script>
  <script>
    function updateWeight() {
      $.get("/api/weight", function(res) {
        if (res.success) {
          $("#weight").text(res.weight.toFixed(2));
          $("#time").text("Updated at: " + res.timestamp);
        } else {
          $("#weight").text("--");
          $("#time").text("No data");
        }
      });
    }

    updateWeight();
    setInterval(updateWeight, 1000);
  </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/api/push_weight", methods=["POST"])
def push_weight():
    global current_weight, last_update_time
    data = request.get_json()

    if "weight" not in data:
        return jsonify(success=False, message="Missing 'weight' field"), 400

    try:
        current_weight = float(data["weight"])
        last_update_time = time.strftime("%Y-%m-%d %H:%M:%S")

        # Save to database
        insert_record(current_weight, last_update_time)

        print(f"[RECEIVED] Weight: {current_weight} g")
        return jsonify(success=True)
    except ValueError:
        return jsonify(success=False, message="Invalid weight format"), 400

@app.route("/api/weight", methods=["GET"])
def get_weight():
    if current_weight is None:
        return jsonify(success=False, message="No data received yet")
    return jsonify(success=True, weight=current_weight, timestamp=last_update_time)

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
