# FOFOCA Software Stack

> Complete software components, configuration, and deployment guide.

---

## Overview

FOFOCA's software is distributed across three tiers: the robot (RPi5 + co-processors), the local server, and the ThinkNEO cloud. All tiers communicate over standard protocols (MQTT, HTTP, WebSocket).

---

## Tier 1: Robot Software (Raspberry Pi 5)

### Operating System

| Component | Version | Notes |
|---|---|---|
| Raspberry Pi OS | Bookworm 64-bit | Lite (headless) |
| Python | 3.11+ | Main application language |
| ROS2 | Humble Hawksbill | Navigation and robotics framework |

### Vision Pipeline

| Component | Version | Role |
|---|---|---|
| OpenCV | 4.9+ | Image processing, camera interface |
| YOLOv8n (Ultralytics) | 8.1+ | Object detection (nano model for RPi5) |
| InsightFace | 0.7+ | Face detection and recognition |
| NumPy | 1.26+ | Array operations |

**Configuration:**
```yaml
vision:
  camera: insta360_usb
  resolution: 1920x960  # equirectangular
  fps: 10
  detection:
    model: yolov8n
    confidence: 0.5
    classes: [person, dog, cat, package, car]
  face_recognition:
    model: buffalo_l
    threshold: 0.6
    known_faces_dir: /opt/fofoca/faces/
```

### Audio Pipeline (Raspberry Pi Zero 2 W)

| Component | Version | Role |
|---|---|---|
| faster-whisper | 0.10+ | Speech-to-text (small model) |
| Piper TTS | 1.2+ | Text-to-speech (pt-BR voice) |
| YAMNet | TFLite | Environmental sound classification |
| PyAudio | 0.2.14 | Audio stream interface |

**Configuration:**
```yaml
audio:
  microphone: respeaker_usb
  sample_rate: 16000
  channels: 1
  stt:
    model: faster-whisper-small
    language: pt
    beam_size: 5
  tts:
    model: piper-pt_BR-faber-medium
    speaker: 0
    rate: 1.0
  sound_classification:
    model: yamnet_tflite
    threshold: 0.7
    alert_classes: [bark, glass_breaking, siren, scream, smoke_alarm]
```

### Navigation (ROS2)

| Component | Version | Role |
|---|---|---|
| ROS2 Humble | 2024.x | Robotics middleware |
| Nav2 | 1.1+ | Autonomous navigation |
| SLAM Toolbox | 2.6+ | Simultaneous localization and mapping |
| robot_localization | 3.5+ | Sensor fusion for odometry |

**Key ROS2 Topics:**
```
/fofoca/cmd_vel          # Velocity commands to track motors
/fofoca/odom             # Odometry from wheel encoders
/fofoca/scan             # Lidar/depth scan for obstacle avoidance
/fofoca/map              # SLAM-generated map
/fofoca/goal_pose        # Navigation goal
/fofoca/camera/image_raw # Raw camera feed
```

### Safety Monitor

| Component | Role |
|---|---|
| Hardware Watchdog | Resets ESP32 if RPi5 stops sending heartbeats |
| Emergency Stop | Kills all motor power on safety trigger |
| Battery Monitor | Reads voltage via ESP32, triggers shutdown at 10.8V |
| Thermal Monitor | Reads RPi5 CPU temp, throttles at 80C |

---

## Tier 2: Local Server Software

### Core Services

| Service | Image/Package | Port | Role |
|---|---|---|---|
| FastAPI Gateway | Python + uvicorn | 8000 | REST API for robot communication |
| MQTT Mosquitto | eclipse-mosquitto:2 | 1883 | Real-time messaging |
| PostgreSQL | postgres:16 | 5432 | State database |
| ChromaDB | chromadb/chroma:latest | 8500 | Vector memory store |
| MinIO | minio/minio:latest | 9000 | Object storage (photos, video) |
| Grafana | grafana/grafana:latest | 3000 | Monitoring dashboards |
| Prometheus | prom/prometheus:latest | 9090 | Metrics collection |
| Ollama | ollama/ollama:latest | 11434 | Local LLM inference |

### Docker Compose (Simplified)

```yaml
version: "3.9"
services:
  mqtt:
    image: eclipse-mosquitto:2
    ports: ["1883:1883"]
    volumes:
      - ./mosquitto/config:/mosquitto/config
      - mosquitto_data:/mosquitto/data

  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: fofoca
      POSTGRES_USER: fofoca
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    ports: ["5432:5432"]
    volumes:
      - pg_data:/var/lib/postgresql/data

  chromadb:
    image: chromadb/chroma:latest
    ports: ["8500:8000"]
    volumes:
      - chroma_data:/chroma/chroma

  minio:
    image: minio/minio:latest
    command: server /data --console-address ":9001"
    ports: ["9000:9000", "9001:9001"]
    volumes:
      - minio_data:/data

  ollama:
    image: ollama/ollama:latest
    ports: ["11434:11434"]
    volumes:
      - ollama_data:/root/.ollama
    deploy:
      resources:
        reservations:
          devices:
            - capabilities: [gpu]

  grafana:
    image: grafana/grafana:latest
    ports: ["3000:3000"]
    volumes:
      - grafana_data:/var/lib/grafana

  prometheus:
    image: prom/prometheus:latest
    ports: ["9090:9090"]
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml

volumes:
  mosquitto_data:
  pg_data:
  chroma_data:
  minio_data:
  ollama_data:
  grafana_data:
```

### Local LLM (Ollama)

```bash
# Pull Nemotron Nano for local inference
ollama pull nemotron-nano

# Test
ollama run nemotron-nano "What should a household robot do if it detects smoke?"
```

The local LLM serves as a fallback when ThinkNEO cloud is unreachable, and handles low-latency tasks that don't require the full Nemotron Ultra 253B model.

---

## Tier 3: ThinkNEO Cloud Integration

### Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `gateway.thinkneo.ai/v1/chat/completions` | POST | Governed inference (OpenAI-compatible) |
| `gateway.thinkneo.ai/v1/embeddings` | POST | Text embeddings for memory |
| `gateway.thinkneo.ai/audit` | POST | Submit audit events |
| `gateway.thinkneo.ai/policies` | GET | Sync governance policies |

### Models Used

| Model | Use Case | Latency |
|---|---|---|
| nvidia/llama-3.1-nemotron-ultra-253b-v1 | Complex reasoning, planning, emergency decisions | 2-5s |
| nvidia/nemotron-nano (local) | Quick responses, classification, simple tasks | 0.1-0.5s |

### Governance Policies

ThinkNEO enforces these policies on every FOFOCA inference request:

```json
{
  "policies": {
    "safety_first": {
      "description": "Emergency actions always take priority",
      "priority": 1
    },
    "action_approval": {
      "description": "Motor commands require policy check",
      "scope": ["motor", "arm", "gripper"]
    },
    "rate_limit": {
      "description": "Max 60 inference requests per minute",
      "limit": 60,
      "window": "1m"
    },
    "content_filter": {
      "description": "Filter inappropriate TTS output",
      "scope": ["tts"]
    },
    "audit_trail": {
      "description": "Log every decision with context",
      "retention": "90d"
    }
  }
}
```

---

## Communication Protocol: MQTT Topics

### Robot -> Server

| Topic | Payload | Frequency |
|---|---|---|
| `fofoca/telemetry/battery` | `{"voltage": 12.1, "percent": 75}` | Every 30s |
| `fofoca/telemetry/position` | `{"x": 3.2, "y": 1.5, "theta": 0.8}` | Every 1s |
| `fofoca/telemetry/temperature` | `{"cpu": 55, "ambient": 24}` | Every 60s |
| `fofoca/vision/detections` | `[{"class": "dog", "confidence": 0.92}]` | Every 100ms |
| `fofoca/audio/events` | `{"type": "bark", "confidence": 0.85}` | On event |
| `fofoca/status` | `{"state": "patrol", "task": "security"}` | On change |

### Server -> Robot

| Topic | Payload | Description |
|---|---|---|
| `fofoca/command/move` | `{"linear": 0.5, "angular": 0.0}` | Movement command |
| `fofoca/command/arm` | `{"joint": 2, "angle": 90}` | Arm joint command |
| `fofoca/command/speak` | `{"text": "Hello!", "lang": "pt"}` | TTS command |
| `fofoca/command/navigate` | `{"x": 5.0, "y": 2.0}` | Navigate to point |
| `fofoca/command/stop` | `{}` | Emergency stop |
| `fofoca/config/update` | `{...}` | Configuration update |

---

## Python Dependencies (RPi5)

```txt
# requirements.txt
openai>=1.30.0
fastapi>=0.111.0
uvicorn>=0.29.0
paho-mqtt>=2.1.0
opencv-python-headless>=4.9.0
ultralytics>=8.1.0
insightface>=0.7.3
onnxruntime>=1.17.0
numpy>=1.26.0
Pillow>=10.3.0
pydantic>=2.7.0
httpx>=0.27.0
python-dotenv>=1.0.0
psutil>=5.9.0
```

---

## Environment Variables

```bash
# ThinkNEO
THINKNEO_KEY=tn_live_...
THINKNEO_BASE_URL=https://gateway.thinkneo.ai/v1

# Local Server
MQTT_HOST=<ROBOT_LAN_IP>
MQTT_PORT=1883
MQTT_USER=fofoca
MQTT_PASS=...

# Database
POSTGRES_HOST=<ROBOT_LAN_IP>
POSTGRES_DB=fofoca
POSTGRES_USER=fofoca
POSTGRES_PASSWORD=...

# Storage
MINIO_ENDPOINT=<ROBOT_LAN_IP>:9000
MINIO_ACCESS_KEY=...
MINIO_SECRET_KEY=...

# ChromaDB
CHROMA_HOST=<ROBOT_LAN_IP>
CHROMA_PORT=8500

# GSM (Emergency)
GSM_PORT=/dev/ttyUSB1
GSM_PIN=1234
EMERGENCY_CONTACTS=+5511999999999
```

---

*Part of the [FOFOCA](https://github.com/thinkneo-ai/fofoca) open study case by [ThinkNEO](https://thinkneo.ai).*
