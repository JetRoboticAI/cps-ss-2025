# Smart Traffic Light System

A modular smart traffic light system leveraging computer vision and IoT protocols to automate traffic management and violation detection.

## Project Structure

```
.
├── backend/                # Backend API and frontend web interface
├── docs/                   # MQTT protocol documentation
├── traffic_light/          # Traffic light control runloop
└── violation_detection/    # Dockerized YOLO & license plate OCR for red light violation detection
```

### Subfolders

- **backend/**: Contains the backend server (API) and frontend web application for system management and monitoring.
- **docs/**: Documentation for MQTT protocols used for communication between system components.
- **traffic_light/**: Implements the main runloop logic for controlling the traffic lights.
- **violation_detection/**: Contains code and Docker setup for running YOLO-based vehicle detection and license plate OCR to identify red light violations.

## Getting Started

### Prerequisites

- Docker (for violation detection)
- Python 3.8+
- Node.js (for frontend, if applicable)

### Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/MiniSmartTraffic.git
    cd MiniSmartTraffic
    ```

2. **Start the backend and frontend:**
    ```bash
    cd backend
    # Follow backend/README.md for setup instructions
    ```

3. **Run the traffic light control:**
    ```bash
    cd ../traffic_light
    python main.py
    ```

4. **Start violation detection:**
    ```bash
    cd ../violation_detection
    docker compose up
    ```

5. **Refer to `docs/` for MQTT protocol details.**

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
