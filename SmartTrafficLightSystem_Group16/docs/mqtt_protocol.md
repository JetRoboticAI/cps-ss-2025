# 🟢 Smart Traffic Light MQTT Protocol Specification

## MQTT Broker Assumptions

* **Broker Type**: HiveMQ
* **Max Payload Size**: ≤10 MB (binary encoded as base64)
* **QoS Levels**:

  * Status Updates: QoS 1 (at least once)
  * Manual Commands: QoS 1 (at least once)
  * Violation Reports: QoS 2 (exactly once)

---

## 1. Traffic Light → MQTT: Current Status Broadcast

**Topic**:

```
traffic_light/<intersection_id>/status
```

**QoS**: `1`

**Payload Format (JSON)**:

```json
{
  "timestamp": "2025-06-04T22:01:00Z",
  "status": "Red",               // "Red", "Green", "Yellow"
  "intersection_id": "0"
}
```

**Example**:

Since we only have one intersection, the `intersection_id` will be `0`.

```json
{
  "timestamp": "2025-06-04T22:01:00Z",
  "status": "Green",
  "intersection_id": "0"
}

```json
{
  "timestamp": "2025-06-04T22:01:00Z",
  "status": "Yellow",
  "intersection_id": "0"
}
```

---

## 2. MQTT → Traffic Light: Manual Control Command

**Topic**:

```
traffic_light/<intersection_id>/command
```

**QoS**: `1`

**Payload Format (JSON)**:

```json
{
  "command": "Red",                      // One of: "Red", "Green", "Yellow", "Auto" ("Auto" means back to auto mode)
  "timeout": 9999,                       // Optional
  "timestamp": "2025-06-04T22:02:30Z",
  "source": "admin_panel"
}
```

**Example**:

```json
{
  "command": "Red",
  "timeout": 9999,
  "timestamp": "2025-06-04T22:02:30Z",
  "source": "remote_operator"
}
```

---

## 3. Violation Detector → MQTT: Violation Report

**Topic**:

```
traffic_violation/<intersection_id>/detected
```

**QoS**: `2`

**Payload Format (JSON)**:

```json
{
  "timestamp": "2025-06-04T22:03:10Z",
  "intersection_id": "0",
  "violation_type": "RED_LIGHT_RUN",    // Constant string
  "license_plate": "ABC1234",
  "confidence": 0.92,
  "image_base64": "<base64-encoded-image-string>",   // ≤10MB after encoding
  "image_format": "jpeg"
}
```

**Example** (truncated base64 string):

```json
{
  "timestamp": "2025-06-04T22:03:10Z",
  "intersection_id": "TL_McMaster_WestGate",
  "violation_type": "RED_LIGHT_RUN",
  "license_plate": "ON4DRIVE",
  "confidence": 0.95,
  "image_base64": "/9j/4AAQSkZJRgABAQEAYABgAAD... (truncated)",
  "image_format": "jpeg"
}
```

**Notes**:

* `image_base64` should be limited in resolution/quality to stay below 10MB.
* Consider preprocessing (e.g., JPEG compression) before encoding.
* For privacy and legal traceability, all timestamps must be in UTC ISO8601.

---

## 📌 Optional Enhancements

* Introduce LWT (`last will and testament`) messages to detect device disconnections.
* Use retained messages for the latest status updates to ensure new subscribers receive the current state immediately.