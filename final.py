#!/usr/bin/env python3
"""
Enhanced Multi-Sensor Client with LED Warning and Stepper Motor Control
水位传感器 + 运动检测 + LED警报 + 步进电机控制
"""
import time
import Adafruit_ADS1x15
import RPi.GPIO as GPIO
import requests
import json
from datetime import datetime
import threading

# ADC配置 (水位传感器)
ADC = Adafruit_ADS1x15.ADS1115()
ADC_CHANNEL = 3
GAIN = 1
MIN_ADC_VALUE = 0
MAX_ADC_VALUE = 32767

# PIR配置 (运动检测传感器)
PIR_PIN = 12

# LED配置 (水位警报灯)
LED_PIN = 16  # 使用GPIO16 (物理引脚36)
WATER_LOW_THRESHOLD = 20.0  # 水位低于20%时点亮LED

# 步进电机配置 (28BYJ-48 + ULN2003)
MOTOR_IN1 = 23
MOTOR_IN2 = 24
MOTOR_IN3 = 25
MOTOR_IN4 = 8
MOTOR_THRESHOLD = 20.0  # 水位低于20%时启动电机
MOTOR_STOP_THRESHOLD = 25.0  # 水位高于25%时停止电机（防止频繁开关）
MOTOR_DELAY = 0.005  # 步进电机每步延迟

# 步进电机序列 (28BYJ-48)
MOTOR_SEQ = [
    [1, 0, 0, 1],
    [1, 0, 0, 0],
    [1, 1, 0, 0],
    [0, 1, 0, 0],
    [0, 1, 1, 0],
    [0, 0, 1, 0],
    [0, 0, 1, 1],
    [0, 0, 0, 1]
]

# GPIO设置
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_PIN, GPIO.IN)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(MOTOR_IN1, GPIO.OUT)
GPIO.setup(MOTOR_IN2, GPIO.OUT)
GPIO.setup(MOTOR_IN3, GPIO.OUT)
GPIO.setup(MOTOR_IN4, GPIO.OUT)

# 初始状态
GPIO.output(LED_PIN, GPIO.LOW)
GPIO.output(MOTOR_IN1, GPIO.LOW)
GPIO.output(MOTOR_IN2, GPIO.LOW)
GPIO.output(MOTOR_IN3, GPIO.LOW)
GPIO.output(MOTOR_IN4, GPIO.LOW)

# 服务器配置
SERVER_URL = "http://192.168.0.118:5000"  # 修改为你的实际IP
API_ENDPOINT = f"{SERVER_URL}/api/sensor_data"

# 全局变量存储最新传感器数据
latest_sensor_data = {
    'water_level': 0,
    'adc_value': 0,
    'motion_detected': False,
    'motion_last_triggered': None,
    'led_warning': False,
    'led_last_activated': None,
    'motor_running': False,
    'motor_last_activated': None,
    'motor_total_runtime': 0,  # 总运行时间（秒）
    'motor_step_count': 0      # 总步数
}

# 电机运行控制
motor_start_time = None
motor_thread = None
motor_running_flag = False

def motor_step(delay, step_sequence):
    """执行一个步进电机步骤"""
    for i in range(4):
        GPIO.output(MOTOR_IN1, step_sequence[i][0])
        GPIO.output(MOTOR_IN2, step_sequence[i][1])
        GPIO.output(MOTOR_IN3, step_sequence[i][2])
        GPIO.output(MOTOR_IN4, step_sequence[i][3])
        time.sleep(delay)

def motor_step_forward(delay, steps):
    """步进电机前进"""
    global latest_sensor_data
    for _ in range(steps):
        if not motor_running_flag:  # 检查是否需要停止
            break
        for seq in MOTOR_SEQ:
            if not motor_running_flag:
                break
            motor_step(delay, [seq])
            latest_sensor_data['motor_step_count'] += 1

def motor_continuous_run():
    """电机连续运行线程"""
    global motor_running_flag, motor_start_time
    print("步进电机开始运行...")
    
    while motor_running_flag:
        # 连续前进运行
        motor_step_forward(MOTOR_DELAY, 50)  # 每次运行50步
        if motor_running_flag:
            time.sleep(0.1)  # 短暂停顿
    
    # 停止时关闭所有电机引脚
    GPIO.output(MOTOR_IN1, GPIO.LOW)
    GPIO.output(MOTOR_IN2, GPIO.LOW)
    GPIO.output(MOTOR_IN3, GPIO.LOW)
    GPIO.output(MOTOR_IN4, GPIO.LOW)
    print("步进电机已停止")

def control_motor(water_level):
    """根据水位控制步进电机"""
    global motor_running_flag, motor_thread, motor_start_time
    
    if water_level < MOTOR_THRESHOLD:
        if not latest_sensor_data['motor_running']:
            # 启动电机
            latest_sensor_data['motor_running'] = True
            latest_sensor_data['motor_last_activated'] = datetime.now().isoformat()
            motor_start_time = time.time()
            motor_running_flag = True
            
            # 启动电机线程
            motor_thread = threading.Thread(target=motor_continuous_run, daemon=True)
            motor_thread.start()
            
            print(f"水位过低！启动步进电机: {water_level:.2f}% < {MOTOR_THRESHOLD}%")
    
    elif water_level >= MOTOR_STOP_THRESHOLD:
        if latest_sensor_data['motor_running']:
            # 停止电机
            motor_running_flag = False
            latest_sensor_data['motor_running'] = False
            
            # 计算运行时间
            if motor_start_time:
                runtime = time.time() - motor_start_time
                latest_sensor_data['motor_total_runtime'] += runtime
                motor_start_time = None
            
            print(f"水位恢复！停止步进电机: {water_level:.2f}% >= {MOTOR_STOP_THRESHOLD}%")

def control_led(water_level):
    """根据水位控制LED灯"""
    if water_level < WATER_LOW_THRESHOLD:
        if not latest_sensor_data['led_warning']:
            # 首次触发警报
            GPIO.output(LED_PIN, GPIO.HIGH)
            latest_sensor_data['led_warning'] = True
            latest_sensor_data['led_last_activated'] = datetime.now().isoformat()
            print(f"水位警报！当前水位: {water_level:.2f}% < {WATER_LOW_THRESHOLD}%，LED已点亮")
        else:
            # 保持点亮状态
            GPIO.output(LED_PIN, GPIO.HIGH)
    else:
        if latest_sensor_data['led_warning']:
            # 水位恢复正常，关闭LED
            GPIO.output(LED_PIN, GPIO.LOW)
            latest_sensor_data['led_warning'] = False
            print(f"水位恢复正常: {water_level:.2f}%，LED已关闭")
        else:
            # 保持关闭状态
            GPIO.output(LED_PIN, GPIO.LOW)

def read_water_level():
    """读取水位传感器数据"""
    try:
        adc_value = ADC.read_adc(ADC_CHANNEL, gain=GAIN)
        water_level = (adc_value - MIN_ADC_VALUE) / (MAX_ADC_VALUE - MIN_ADC_VALUE) * 100
        
        # 确保水位百分比在0-100范围内
        water_level = max(0, min(100, water_level))
        
        # 控制LED警报和步进电机
        control_led(water_level)
        control_motor(water_level)
        
        return {
            'adc_value': adc_value,
            'water_level': round(water_level, 2)
        }
    except Exception as e:
        print(f"读取水位传感器数据失败: {e}")
        return {'adc_value': 0, 'water_level': 0}

def read_motion_sensor():
    """读取运动检测传感器数据"""
    try:
        pir_value = GPIO.input(PIR_PIN)
        motion_detected = pir_value == GPIO.HIGH
        
        if motion_detected:
            print("检测到运动!")
            latest_sensor_data['motion_last_triggered'] = datetime.now().isoformat()
        
        return motion_detected
    except Exception as e:
        print(f"读取运动传感器数据失败: {e}")
        return False

def collect_all_sensor_data():
    """收集所有传感器数据"""
    water_data = read_water_level()
    motion_detected = read_motion_sensor()
    
    # 更新运行时间（如果电机正在运行）
    if latest_sensor_data['motor_running'] and motor_start_time:
        current_runtime = time.time() - motor_start_time
        total_runtime = latest_sensor_data['motor_total_runtime'] + current_runtime
    else:
        total_runtime = latest_sensor_data['motor_total_runtime']
    
    # 更新全局数据
    latest_sensor_data['water_level'] = water_data['water_level']
    latest_sensor_data['adc_value'] = water_data['adc_value']
    latest_sensor_data['motion_detected'] = motion_detected
    
    return {
        'timestamp': datetime.now().isoformat(),
        'sensor_id': 'multi_sensor_with_motor_01',
        'water_level': water_data['water_level'],
        'adc_value': water_data['adc_value'],
        'motion_detected': motion_detected,
        'motion_last_triggered': latest_sensor_data['motion_last_triggered'],
        'led_warning': latest_sensor_data['led_warning'],
        'led_last_activated': latest_sensor_data['led_last_activated'],
        'motor_running': latest_sensor_data['motor_running'],
        'motor_last_activated': latest_sensor_data['motor_last_activated'],
        'motor_total_runtime': round(total_runtime, 2),
        'motor_step_count': latest_sensor_data['motor_step_count']
    }

def send_data_to_server(data):
    """发送数据到服务器"""
    try:
        response = requests.post(
            API_ENDPOINT, 
            json=data, 
            timeout=5,
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code == 200:
            status_msg = f"{data['water_level']:.2f}% {'✓' if data['motion_detected'] else '✗'}"
            if data['led_warning']:
                status_msg += " LED"
            if data['motor_running']:
                status_msg += " MOTOR"
            print(f"数据发送成功: {status_msg}")
            return True
        else:
            print(f"服务器响应错误: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"网络连接失败: {e}")
        return False

def test_components():
    """测试所有组件功能"""
    print("测试LED功能...")
    for i in range(3):
        GPIO.output(LED_PIN, GPIO.HIGH)
        print(f"  LED ON ({i+1}/3)")
        time.sleep(0.5)
        GPIO.output(LED_PIN, GPIO.LOW)
        print(f"  LED OFF ({i+1}/3)")
        time.sleep(0.5)
    
    print("测试步进电机功能...")
    print("  电机前进10步...")
    motor_step_forward(MOTOR_DELAY, 10)
    time.sleep(1)
    
    print("所有组件测试完成")

def main():
    global motor_running_flag, motor_start_time
    
    print("=== 多传感器客户端 + LED警报 + 步进电机系统启动 ===")
    print(f"服务器地址: {SERVER_URL}")
    print(f"监控功能: 水位传感器 + 运动检测 + LED警报 + 步进电机")
    print(f"LED警报引脚: GPIO{LED_PIN}")
    print(f"步进电机引脚: GPIO{MOTOR_IN1},{MOTOR_IN2},{MOTOR_IN3},{MOTOR_IN4}")
    print(f"水位警报阈值: {WATER_LOW_THRESHOLD}%")
    print(f"电机启动阈值: {MOTOR_THRESHOLD}%，停止阈值: {MOTOR_STOP_THRESHOLD}%")
    
    # 测试组件
    test_components()
    
    try:
        while True:
            # 收集所有传感器数据
            sensor_data = collect_all_sensor_data()
            
            # 本地显示
            status_line = f"ADC: {sensor_data['adc_value']}, 水位: {sensor_data['water_level']:.2f}%, 运动: {'是' if sensor_data['motion_detected'] else '否'}"
            if sensor_data['led_warning']:
                status_line += " [LED警报]"
            if sensor_data['motor_running']:
                status_line += f" [电机运行-{sensor_data['motor_step_count']}步]"
            print(status_line)
            
            # 发送到服务器
            send_data_to_server(sensor_data)
            
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n程序被用户终止")
    except Exception as e:
        print(f"程序运行错误: {e}")
    finally:
        # 停止电机
        motor_running_flag = False
        if motor_thread and motor_thread.is_alive():
            motor_thread.join(timeout=2)
        
        # 清理GPIO
        GPIO.output(LED_PIN, GPIO.LOW)
        GPIO.output(MOTOR_IN1, GPIO.LOW)
        GPIO.output(MOTOR_IN2, GPIO.LOW)
        GPIO.output(MOTOR_IN3, GPIO.LOW)
        GPIO.output(MOTOR_IN4, GPIO.LOW)
        GPIO.cleanup()
        print("GPIO已清理，程序安全退出")

if __name__ == "__main__":
    main()