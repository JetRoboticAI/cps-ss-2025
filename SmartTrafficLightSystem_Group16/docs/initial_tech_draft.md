
## Current Progress:

- Circuit built
    
- Tested NCNN framework inference using Docker container with YOLOv11
    
- Camera connectivity validated (**sliver/gold connector should face to the ethernet port**)
    
- `/home/yifei/sep769-iot-project/` provided sample code
    

### Test NCNN Inference

```bash
t=ultralytics/ultralytics:latest-arm64 && sudo docker pull $t && sudo docker run -it --ipc=host $t
# Export a YOLOv11n PyTorch model to NCNN format
yolo export model=yolo11n.pt format=ncnn # creates 'yolo11n_ncnn_model'

# Run inference with the exported model
yolo predict model='yolo11n_ncnn_model' source='https://ultralytics.com/images/bus.jpg'
```

Source:  
[https://docs.ultralytics.com/guides/raspberry-pi/#__tabbed_4_1](https://docs.ultralytics.com/guides/raspberry-pi/#__tabbed_4_1)

If you would like to test for real-time video object detection:

```bash
rpicam-vid -n -t 0 --inline --listen -o tcp://0.0.0.0:8888

# In another terminal, open Docker container
t=ultralytics/ultralytics:latest-arm64 && sudo docker pull $t && sudo docker run -it --ipc=host --net="host" $t

yolo export model=yolo11n.pt format=ncnn # creates 'yolo11n_ncnn_model'

yolo predict model='yolo11n_ncnn_model' source="tcp://127.0.0.1:8888"
```

---

## Process Workflow:

The traffic light system is implemented as a separate process. It first registers a handler to subscribe to MQTT messages, then enters a runloop. In each runloop iteration, it checks for new control commands received via the MQTT message handler. If the state changes, it publishes the updated state via MQTT.

### Available Statuses:

- Normal Red
- Normal Amber
- Normal Green
- Flashing Red
- Flashing Yellow

### LED Control:

LEDs (GPIO output) are switched based on the current state. Today, the breadboard is not provided, but the program logic runs without GPIO output.  
GPIO 2, 3, 4 correspond to physical pins 3, 5, 7.

---

## Traffic Light Violation Detection Process:

This is another separate process. It can acquire the red light state via:
    
- **Local socket connection (recommended)** to the traffic light process
- **Local RPC call** to query the state every 0.2–0.5 seconds
- **RESTful API** to query the state every 0.2–0.5 seconds

### Process:

- If the state is Red, start the camera and begin capturing.
- Can use OpenCV’s `open_device` API to capture until the light turns Green.
- **Detect motion?** (OpenCV-based motion detection optional, for optimization)
- Feed video stream or captured images directly to the YOLO model
- **YOLOv8/v11 retraining needed?**
    - YOLOv11 will run in a separate process (Docker container), since installing `ultralytics[export]` natively on Raspberry Pi is time-consuming (not succeed).
    - Recommend writing a Dockerfile based on `ultralytics/ultralytics-arm64`, install Python Flask framework, and expose an API to handle image processing via queue and return results as JSON. This acts as a separate microservice callable by the traffic violation process.
    - If a vehicle is detected (via bounding boxes):
        - Call an OCR API to extract the license plate (local deployment TBD)
        - Submit data to backend via MQTT (with consideration for network outage handling)

---

## Backend:

### Process:

- Subscribes to traffic light state updates
- Subscribes to traffic violation detection results
- Serves API for frontend to display results
    