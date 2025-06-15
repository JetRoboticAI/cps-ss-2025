from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime
import json
import paho.mqtt.publish as publish
app = Flask(__name__)
CORS(app)  

DB_FILE = os.path.join(os.path.dirname(__file__), "traffic_data.db")
print("--------------------------------------")
print("[DEBUG] Using DB file:", os.path.abspath(DB_FILE))

def get_latest_light_status():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT intersection_id, status, timestamp
        FROM light_status
        WHERE id IN (
            SELECT MAX(id) FROM light_status GROUP BY intersection_id
        )
    ''')
    rows = cursor.fetchall()
    conn.close()

    result = []
    for row in rows:
        result.append({
            "intersection_id": row[0],
            "status": row[1],   # e.g., "RED", "GREEN", "YELLOW"
            "timestamp": row[2]
        })

    return result

def get_paginated_violations(page=1, limit=6):
    offset = (page - 1) * limit

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM violations")
    total = cursor.fetchone()[0]

    cursor.execute('''
        SELECT id, timestamp, type, plate, location, image_base64
        FROM violations
        ORDER BY id DESC
        LIMIT ? OFFSET ?
    ''', (limit, offset))
    rows = cursor.fetchall()
    conn.close()

    result = []
    for row in rows:
        result.append({
            "id": row[0],
            "timestamp": row[1],
            "type": row[2],
            "plate": row[3],
            "location": row[4],
            "image": row[5]
        })

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "data": result
    }

@app.route('/api/light_status/<intersection_id>')
def api_light_status(intersection_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT status, timestamp
        FROM light_status
        WHERE intersection_id = ?
        ORDER BY id DESC
        LIMIT 1
    ''', (intersection_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return jsonify({
            "intersection_id": intersection_id,
            "status": row[0],
            "timestamp": row[1]
        })
    else:
        return jsonify({
            "intersection_id": intersection_id,
            "status": "Unknown",
            "timestamp": None
        }), 404

@app.route('/api/violations')
def api_violations():
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 6))
    except ValueError:
        page = 1
        limit = 6

    data = get_paginated_violations(page, limit)
    return jsonify(data)

@app.route('/api/lights')
def api_lights():
    data = get_latest_light_status()
    return jsonify({
        "total": len(data),
        "data": data
    })

@app.route('/api/control', methods=['POST'])
def api_control():
    data = request.json
    command = data.get('command')
    intersection_id = data.get('intersection_id', '0')  

    timeouts = {
        "Red": 30,
        "Green": 30,
        "Yellow": 10,
        "Auto": 1  
    }

    if command not in timeouts:
        return jsonify({"error": "Invalid command"}), 400

    #real_command = "Green" if command == "Auto" else command
    timeout = timeouts[command]

    payload = {
        #"command": real_command,
        "command": command,
        "timeout": timeout,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "source": "admin_panel"
    }

    topic = f"traffic_light/{intersection_id}/command"

    try:
        publish.single(
            topic,
            payload=json.dumps(payload),
            hostname="mqtt-dashboard.com",
            port=1883
        )
        return jsonify({"success": True, "sent": payload})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("[Flask] Running on http://localhost:5000")
    app.run(debug=True)
