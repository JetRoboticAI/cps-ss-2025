"""
Multi-Sensor Dashboard Server with LED Warning Support
接收水位、运动检测和LED警报数据并提供Web界面
"""
from flask import Flask, render_template, jsonify, request
import sqlite3
import json
from datetime import datetime, timedelta
import threading
import time

app = Flask(__name__)

# 数据库初始化
def init_database():
    conn = sqlite3.connect('sensor_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensor_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            adc_value INTEGER NOT NULL,
            water_level REAL NOT NULL,
            motion_detected BOOLEAN NOT NULL,
            motion_last_triggered TEXT,
            led_warning BOOLEAN DEFAULT 0,
            led_last_activated TEXT,
            sensor_id TEXT NOT NULL
        )
    ''')
    
    # 检查并添加LED字段（如果不存在）
    cursor.execute("PRAGMA table_info(sensor_readings)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'led_warning' not in columns:
        print("添加 led_warning 字段到数据库...")
        cursor.execute('ALTER TABLE sensor_readings ADD COLUMN led_warning BOOLEAN DEFAULT 0')
    
    if 'led_last_activated' not in columns:
        print("添加 led_last_activated 字段到数据库...")
        cursor.execute('ALTER TABLE sensor_readings ADD COLUMN led_last_activated TEXT')
    
    conn.commit()
    conn.close()
    print("数据库初始化完成")

# 保存数据到数据库
def save_sensor_data(data):
    try:
        conn = sqlite3.connect('sensor_data.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO sensor_readings (timestamp, adc_value, water_level, motion_detected, 
                                       motion_last_triggered, led_warning, led_last_activated, sensor_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['timestamp'], 
            data['adc_value'], 
            data['water_level'], 
            data['motion_detected'],
            data.get('motion_last_triggered'),
            data.get('led_warning', False),
            data.get('led_last_activated'),
            data['sensor_id']
        ))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"数据库保存错误: {e}")
        return False

# 获取最新数据
def get_latest_data():
    try:
        conn = sqlite3.connect('sensor_data.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT timestamp, adc_value, water_level, motion_detected, motion_last_triggered, 
                   led_warning, led_last_activated, sensor_id
            FROM sensor_readings
            ORDER BY id DESC
            LIMIT 1
        ''')
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'timestamp': result[0],
                'adc_value': result[1],
                'water_level': result[2],
                'motion_detected': bool(result[3]),
                'motion_last_triggered': result[4],
                'led_warning': bool(result[5]) if result[5] is not None else False,
                'led_last_activated': result[6],
                'sensor_id': result[7],
                'status': 'online'
            }
        else:
            return {'status': 'no_data'}
    except Exception as e:
        print(f"获取数据错误: {e}")
        return {'status': 'error'}

# 获取历史数据
def get_historical_data(hours=24):
    try:
        conn = sqlite3.connect('sensor_data.db')
        cursor = conn.cursor()
        
        since_time = (datetime.now() - timedelta(hours=hours)).isoformat()
        cursor.execute('''
            SELECT timestamp, water_level, motion_detected, led_warning
            FROM sensor_readings
            WHERE timestamp > ?
            ORDER BY timestamp ASC
        ''', (since_time,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'timestamp': row[0], 
                'water_level': row[1],
                'motion_detected': bool(row[2]),
                'led_warning': bool(row[3]) if row[3] is not None else False
            } for row in results
        ]
    except Exception as e:
        print(f"获取历史数据错误: {e}")
        return []

# 获取运动检测统计
def get_motion_stats(hours=24):
    try:
        conn = sqlite3.connect('sensor_data.db')
        cursor = conn.cursor()
        
        since_time = (datetime.now() - timedelta(hours=hours)).isoformat()
        cursor.execute('''
            SELECT COUNT(*) as total_readings,
                   SUM(CASE WHEN motion_detected = 1 THEN 1 ELSE 0 END) as motion_detections
            FROM sensor_readings
            WHERE timestamp > ?
        ''', (since_time,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0] > 0:
            total_readings = result[0]
            motion_detections = result[1]
            motion_percentage = (motion_detections / total_readings) * 100
            return {
                'total_readings': total_readings,
                'motion_detections': motion_detections,
                'motion_percentage': round(motion_percentage, 2)
            }
        else:
            return {'total_readings': 0, 'motion_detections': 0, 'motion_percentage': 0}
    except Exception as e:
        print(f"获取运动统计错误: {e}")
        return {'total_readings': 0, 'motion_detections': 0, 'motion_percentage': 0}

# 获取LED警报统计
def get_led_warning_stats(hours=24):
    try:
        conn = sqlite3.connect('sensor_data.db')
        cursor = conn.cursor()
        
        since_time = (datetime.now() - timedelta(hours=hours)).isoformat()
        cursor.execute('''
            SELECT COUNT(*) as total_readings,
                   SUM(CASE WHEN led_warning = 1 THEN 1 ELSE 0 END) as warning_count,
                   MIN(CASE WHEN led_warning = 1 THEN water_level ELSE NULL END) as min_water_level
            FROM sensor_readings
            WHERE timestamp > ?
        ''', (since_time,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0] > 0:
            total_readings = result[0]
            warning_count = result[1] or 0
            min_water_level = result[2]
            warning_percentage = (warning_count / total_readings) * 100
            return {
                'total_readings': total_readings,
                'warning_count': warning_count,
                'warning_percentage': round(warning_percentage, 2),
                'min_water_level': min_water_level
            }
        else:
            return {'total_readings': 0, 'warning_count': 0, 'warning_percentage': 0, 'min_water_level': None}
    except Exception as e:
        print(f"获取LED警报统计错误: {e}")
        return {'total_readings': 0, 'warning_count': 0, 'warning_percentage': 0, 'min_water_level': None}

# API路由
@app.route('/api/sensor_data', methods=['POST'])
def receive_sensor_data():
    try:
        data = request.json
        if save_sensor_data(data):
            return jsonify({'status': 'success', 'message': '数据保存成功'})
        else:
            return jsonify({'status': 'error', 'message': '数据保存失败'}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/latest')
def api_latest_data():
    return jsonify(get_latest_data())

@app.route('/api/history')
def api_historical_data():
    hours = request.args.get('hours', 24, type=int)
    return jsonify(get_historical_data(hours))

@app.route('/api/motion_stats')
def api_motion_stats():
    hours = request.args.get('hours', 24, type=int)
    return jsonify(get_motion_stats(hours))

@app.route('/api/led_warning_stats')
def api_led_warning_stats():
    hours = request.args.get('hours', 24, type=int)
    return jsonify(get_led_warning_stats(hours))

# Web界面路由
@app.route('/')
def dashboard():
    return render_template('dashboard.html')

# 清理旧数据
def cleanup_old_data():
    while True:
        try:
            conn = sqlite3.connect('sensor_data.db')
            cursor = conn.cursor()
            week_ago = (datetime.now() - timedelta(days=7)).isoformat()
            cursor.execute('DELETE FROM sensor_readings WHERE timestamp < ?', (week_ago,))
            conn.commit()
            conn.close()
            print(f"清理了旧数据")
        except Exception as e:
            print(f"清理数据错误: {e}")
        
        time.sleep(3600)

if __name__ == '__main__':
    # 初始化数据库
    init_database()
    
    # 启动数据清理线程
    cleanup_thread = threading.Thread(target=cleanup_old_data, daemon=True)
    cleanup_thread.start()
    
    print("多传感器Dashboard服务器启动中...")
    print("监控传感器: 水位传感器 + 运动检测 + LED警报")
    print("访问地址: http://localhost:5000")
    
    # 启动Flask服务器
    app.run(host='0.0.0.0', port=5000, debug=True)