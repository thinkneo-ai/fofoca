# FOFOCA Architecture

> Detailed architecture document for the FOFOCA autonomous household robot.

---

## Overview

FOFOCA follows a **three-tier architecture** where sensor data flows upward through processing layers and commands flow downward through governance layers. ThinkNEO sits at the top of the governance chain, ensuring every decision is policy-compliant, logged, and auditable.

```
┌─────────────────────────────────────────────────────────────────┐
│                    TIER 3: CLOUD GOVERNANCE                      │
│                                                                  │
│  ThinkNEO Control Plane (gateway.thinkneo.ai)                   │
│  ├── Policy Engine         — action approval / denial            │
│  ├── Audit Logger          — immutable event log                 │
│  ├── Usage Tracker         — token / cost accounting             │
│  ├── Nemotron Ultra 253B   — complex reasoning (cloud)           │
│  └── Observability         — metrics, traces, alerts             │
│                                                                  │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTPS / WebSocket
┌──────────────────────────┴──────────────────────────────────────┐
│                    TIER 2: LOCAL SERVER                           │
│                                                                  │
│  Ubuntu 24.04 LTS (16GB+ RAM)                                   │
│  ├── FastAPI Gateway       — REST API for robot <-> server       │
│  ├── MQTT Mosquitto        — real-time pub/sub messaging         │
│  ├── Nemotron Nano (Ollama)— local LLM for low-latency tasks    │
│  ├── ChromaDB              — vector memory store                 │
│  ├── PostgreSQL            — relational state database           │
│  ├── MinIO                 — object storage (photos, video)      │
│  ├── Grafana + Prometheus  — monitoring dashboards               │
│  └── Flutter App Server    — serves mobile control app           │
│                                                                  │
└──────────────────────────┬──────────────────────────────────────┘
                           │ WiFi (2.4GHz / 5GHz)
┌──────────────────────────┴──────────────────────────────────────┐
│                    TIER 1: ROBOT (ON-BOARD)                       │
│                                                                  │
│  Raspberry Pi 5 (Main Brain)                                     │
│  ├── Vision Pipeline       — OpenCV + YOLOv8n + InsightFace      │
│  ├── Decision Engine       — task scheduling, state machine       │
│  ├── ROS2 Humble           — navigation, SLAM, path planning     │
│  ├── Safety Monitor        — hardware watchdog, emergency stop    │
│  └── Communication Layer   — MQTT client, FastAPI client          │
│                                                                  │
│  Raspberry Pi Zero 2 W (Audio Co-processor)                      │
│  ├── faster-whisper        — speech-to-text                       │
│  ├── Piper TTS             — text-to-speech                       │
│  ├── YAMNet               — environmental sound classification    │
│  └── Wake Word Engine      — always-on voice activation           │
│                                                                  │
│  Microcontrollers                                                │
│  ├── ESP32                 — track motors, BT, sensor fusion      │
│  ├── RP2040 Pico           — servo PWM (6 arm + 1 gripper)       │
│  ├── Arduino Mega 2560     — sensor hub (analog + digital)        │
│  ├── Arduino Uno R4 WiFi   — status LEDs, buzzer, aux I/O        │
│  └── ESP8266 + OLED        — status display module                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Communication Protocols

### Robot <-> Local Server

| Protocol | Use Case | Port |
|---|---|---|
| MQTT (Mosquitto) | Real-time telemetry, commands, sensor data | 1883 |
| HTTP (FastAPI) | API calls, file uploads, configuration | 8000 |
| WebSocket | Live camera feed streaming | 8001 |

### Local Server <-> ThinkNEO Cloud

| Protocol | Use Case | Endpoint |
|---|---|---|
| HTTPS | Governed inference (Nemotron Ultra) | gateway.thinkneo.ai/v1 |
| HTTPS | Audit log submission | gateway.thinkneo.ai/audit |
| HTTPS | Policy sync | gateway.thinkneo.ai/policies |
| WebSocket | Real-time governance events | gateway.thinkneo.ai/ws |

### On-Board (RPi5 <-> Microcontrollers)

| Protocol | Use Case | Bus |
|---|---|---|
| UART/Serial | ESP32 motor commands | /dev/ttyUSB0 |
| I2C | RP2040 servo commands, sensor reads | GPIO 2/3 |
| SPI | High-speed sensor data | GPIO 10/11 |
| USB | Insta360 camera, USB mic | USB 3.0 |
| Bluetooth | Speaker audio output | BT 5.0 |
| GPIO | Direct digital I/O, interrupts | Various |

---

## Data Flow

### Perception Loop (10 Hz)

```
Insta360 Camera ──> RPi5 (OpenCV) ──> YOLOv8n Detection
                                         │
                                         ├──> Object List
                                         ├──> Face Embeddings (InsightFace)
                                         └──> Scene Description
                                                │
                                                ▼
                                         Decision Engine
                                                │
                                         ┌──────┴──────┐
                                         │             │
                                    Local Task    Cloud Reasoning
                                    (immediate)   (ThinkNEO)
```

### Command Loop (Variable Frequency)

```
Decision Engine ──> MQTT Publish ──> Topic Router
                                        │
                    ┌───────────────────┼───────────────────┐
                    │                   │                   │
              fofoca/motor        fofoca/arm          fofoca/audio
                    │                   │                   │
                  ESP32              RP2040            RPi Zero 2W
                    │                   │                   │
              Track Motors        Servo Array         Speaker/TTS
```

### Governance Loop (Every Decision)

```
Robot Decision ──> Local Server ──> ThinkNEO Policy Check
                                         │
                                    ┌────┴────┐
                                    │         │
                                 APPROVED   DENIED
                                    │         │
                                 Execute    Log + Alert
                                    │
                               Audit Trail
```

---

## Module Responsibilities

### RPi5 — Main Brain

- Runs the main decision engine (Python 3.11)
- Processes camera frames via OpenCV + YOLOv8n
- Manages ROS2 navigation stack
- Communicates with all microcontrollers
- Handles WiFi connectivity to local server

### RPi Zero 2 W — Audio Co-processor

- Always-on microphone monitoring
- Wake word detection (custom model)
- Speech-to-text via faster-whisper (small model)
- Text-to-speech via Piper TTS
- Sound classification via YAMNet (barking, glass breaking, alarms)

### ESP32 — Motor & Sensor Controller

- Dual track motor control via HW130 driver
- IMU / accelerometer reading for orientation
- Ultrasonic distance sensors for obstacle detection
- Bluetooth audio streaming to speaker
- Battery voltage monitoring (ADC)

### RP2040 Pico — Arm Controller

- 6-channel PWM for MG90S servos
- Gripper open/close control
- Inverse kinematics calculation for arm positioning
- Calibration routines and safety limits

### Arduino Mega 2560 — Sensor Hub

- Temperature, humidity, gas sensors
- Light level sensors
- Door/window magnetic sensors
- PIR motion sensors
- Analog sensor multiplexing

### Arduino Uno R4 WiFi — Aux Interface

- Status LED array (RGB)
- Piezo buzzer for alerts
- Button inputs for manual override
- WiFi backup channel

### ESP8266 + OLED — Status Display

- Shows current task / mood
- Battery percentage
- WiFi signal strength
- Error codes

---

## Failsafe Hierarchy

FOFOCA implements a strict failsafe hierarchy. If any tier fails, the lower tier takes over:

1. **ThinkNEO Cloud unavailable** -> Local server handles decisions using Nemotron Nano
2. **Local server unavailable** -> RPi5 runs in autonomous mode with cached policies
3. **WiFi lost** -> GSM fallback (SIM800L) for emergency calls only
4. **RPi5 crash** -> ESP32 hardware watchdog stops all motors, sounds alarm
5. **Battery critical (<10%)** -> Navigate to charging station, shutdown non-essential systems
6. **Battery dead** -> All systems off; resume on power restore

---

## Security Model

- All ThinkNEO API calls use TLS 1.3
- API keys stored in environment variables, never in code
- MQTT uses authentication (username/password)
- Local server runs in a private network (no public ports)
- Camera footage is encrypted at rest in MinIO
- Face embeddings are stored locally only (never sent to cloud)
- GSM module is SIM-locked to prevent unauthorized use

---

*Part of the [FOFOCA](https://github.com/thinkneo-ai/fofoca) open study case by [ThinkNEO](https://thinkneo.ai).*
