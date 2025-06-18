# Smart Traffic Light System

A modular smart traffic light system leveraging computer vision and IoT protocols to automate traffic management and violation detection.

## Project Structure

```
.
├── backend/                # Backend API
├── docs/                   # MQTT protocol documentation
├── traffic_light/          # Traffic light control runloop
├── traffic_light_web/      # Vue.js frontend interface
└── violation_detection/    # Dockerfile for license plate OCR and service for red light violation detection
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
    ```bash
    cd ../traffic_light_web
    npm run serve
    ```

3. **Run the traffic light control:**
    ```bash
    cd ../traffic_light
    python main.py
    ```

4. **Start violation detection:**
   
   Build the docker image using the Dockerfile in `violation_detection` and spin up an container on a x86_64 machine using the built image exposing `5000` to the host as the numberplate recognition API.
    ```bash
    cd ../violation_detection
    uv run main.py
    ```

5. **Refer to `docs/` for MQTT protocol details.**

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
