<p align="center">
  <img src="https://img.shields.io/badge/ThinkNEO-Study%20Case-blueviolet?style=for-the-badge" alt="ThinkNEO Study Case" />
  <img src="https://img.shields.io/badge/NVIDIA-Inception%20Program-76B900?style=for-the-badge&logo=nvidia&logoColor=white" alt="NVIDIA Inception" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="MIT License" />
  <img src="https://img.shields.io/badge/Hardware-Open%20Source-orange?style=for-the-badge" alt="Open Source Hardware" />
  <img src="https://img.shields.io/badge/Status-Active%20Development-blue?style=for-the-badge" alt="Active Development" />
</p>

<h1 align="center">FOFOCA</h1>

<h3 align="center">Fully Operational Feline-free Omniscient Companion Assistant</h3>

<p align="center">
  <strong>An open-source autonomous household robot governed by ThinkNEO Enterprise AI Control Plane</strong>
</p>

<p align="center">
  <a href="https://thinkneorobotics.online">Live Site</a> &bull;
  <a href="docs/architecture.md">Architecture</a> &bull;
  <a href="docs/bill-of-materials.md">Bill of Materials</a> &bull;
  <a href="docs/power-system.md">Power System</a> &bull;
  <a href="docs/software-stack.md">Software Stack</a>
</p>

---

## What is FOFOCA?

**FOFOCA** is a fully autonomous household robot built from commodity hardware and governed end-to-end by [ThinkNEO](https://thinkneo.ai) — an Enterprise AI Control Plane. It is a real, physical machine designed to operate 24/7 inside a residential environment, performing tasks that range from pet monitoring and delivery reception to home security and emergency response.

FOFOCA is published as an **official ThinkNEO study case** to demonstrate that the same governance, observability, and multi-agent orchestration used to manage cloud AI agents can govern physical robotics in the real world.

The entire stack runs on NVIDIA technology — from Nemotron Ultra 253B for reasoning to YOLOv8 for vision to Piper TTS for speech — all routed through the ThinkNEO control plane.

### Key Principles

- **Full Governance** — Every decision the robot makes is logged, auditable, and governed by ThinkNEO policies
- **Commodity Hardware** — Built from off-the-shelf components anyone can purchase (total BOM under $600)
- **100% NVIDIA Stack** — Inference powered by NVIDIA Nemotron models via ThinkNEO gateway
- **Open Source** — Hardware design, software, and architecture are fully open under MIT license
- **Real-World Operation** — Not a demo; designed for continuous 24/7 autonomous operation

---

## Why FOFOCA Exists

Enterprise AI governance platforms typically manage cloud-based agents — chatbots, copilots, workflow automations. FOFOCA proves that **ThinkNEO governance extends to the physical world**:

| Cloud Governance | Physical Governance (FOFOCA) |
|---|---|
| Rate limiting API calls | Power budget management |
| Prompt injection detection | Sensor spoofing detection |
| Agent output auditing | Action auditing (motor commands, speech) |
| Multi-tenant isolation | Room-level access control |
| SLA monitoring | Real-time safety monitoring |
| Cost tracking | Battery & energy tracking |

Every motor command, every camera frame analyzed, every word spoken by FOFOCA passes through ThinkNEO's governance layer. If the control plane says stop, the robot stops.

---

## Bill of Materials

### Compute & Control

| Component | Role | Qty | Est. Price |
|---|---|---|---|
| Raspberry Pi 5 8GB | Main brain — runs vision, AI inference client, ROS2 | 1 | $80 |
| Raspberry Pi Zero 2 W | Co-processor — audio pipeline, TTS, wake word | 1 | $15 |
| RP2040 Pico | Robotic arm PWM controller (6 servos + gripper) | 1 | $4 |
| ESP32 DevKit V1 | Track motor control, sensor aggregation, Bluetooth | 1 | $8 |
| Arduino Mega 2560 | Sensor hub — manages all analog/digital sensor inputs | 1 | $15 |
| Arduino Uno R4 WiFi | Auxiliary interface — status LEDs, buzzer, aux I/O | 1 | $27 |

### Sensors & Perception

| Component | Role | Qty | Est. Price |
|---|---|---|---|
| Insta360 X3/X4 | 360-degree vision — panoramic environment awareness | 1 | $300 |
| ReSpeaker USB Mic Array | Audio input — 4-mic array for far-field voice capture | 1 | $30 |
| ESP8266 + 0.96" OLED | Status display — shows mood, battery, current task | 1 | $6 |
| Keystudio IO Expander v5.0 | I/O expansion — additional GPIO for sensors/actuators | 1 | $12 |

### Locomotion & Actuators

| Component | Role | Qty | Est. Price |
|---|---|---|---|
| MG90S Micro Servo | Robotic arm joints (shoulder, elbow, wrist, base, tilt) | 6 | $18 |
| Gripper Kit | End effector — pick and place for deliveries/objects | 1 | $8 |
| Tank Track Chassis Kit | Tractor-style tracked locomotion — all-surface indoor | 1 | $35 |
| HW130 Motor Driver | DC motor driver for track motors (dual H-bridge) | 1 | $5 |
| Microstep Driver (A4988/DRV8825) | Precision stepper control for arm base rotation | 1 | $4 |
| Bluetooth Speaker (3W) | Audio output — speech, alerts, notifications | 1 | $10 |

### Power

| Component | Role | Qty | Est. Price |
|---|---|---|---|
| Zircon 12V 6Ah LiFePO4 Battery | Main power source — 72Wh, >500 cycles | 1 | $45 |
| LM2596 Buck Converter | Voltage regulation — 12V to 5V/3.3V rails | 5 | $5 |
| SIM800L GSM Module | Cellular fallback — SMS alerts when WiFi fails | 1 | $8 |

### Local Server

| Component | Role | Est. Price |
|---|---|---|
| Any PC / Gaming PC (16GB+ RAM) | Local inference server — runs Nemotron Nano, ChromaDB, MQTT | Varies |
| Ubuntu Server 24.04 LTS | Operating system for local server | Free |

### Software (All Free / Open Source)

| Component | Role |
|---|---|
| ThinkNEO Control Plane | Governance, observability, multi-agent orchestration |
| OpenCV + YOLOv8n + InsightFace | Vision pipeline — object detection, face recognition |
| YAMNet + faster-whisper + Piper TTS | Audio pipeline — sound classification, STT, TTS |
| ROS2 Humble + Nav2 SLAM | Navigation — mapping, path planning, obstacle avoidance |
| Nemotron Ultra 253B (via ThinkNEO) | Cloud reasoning — complex decisions, planning |
| Nemotron Nano (local via Ollama) | Local reasoning — low-latency, offline-capable |
| ChromaDB + PostgreSQL + MinIO | Memory — vector store, relational data, object storage |
| FastAPI + MQTT Mosquitto | Communications — REST API + real-time messaging |
| Flutter Mobile App | User interface — remote control, camera feed, status |
| Grafana + Prometheus | Monitoring — dashboards, alerts, metrics |

**Estimated total hardware cost: ~$560 USD** (excluding local server PC and Insta360 camera)

---

## Architecture

```
                          +---------------------------+
                          |    ThinkNEO Cloud         |
                          |    Control Plane          |
                          |  gateway.thinkneo.ai/v1   |
                          +--+----+----+----+----+---+
                             |    |    |    |    |
                    Governance|   |Logs |Metrics|  |Policy
                             |    |    |    |    |
              +--------------+----+----+----+----+--------------+
              |              LOCAL SERVER (Ubuntu)               |
              |                                                  |
              |  +----------+  +----------+  +----------+       |
              |  |Nemotron  |  |ChromaDB  |  |PostgreSQL|       |
              |  |Nano/Ollama| |Vectors   |  |State DB  |       |
              |  +----------+  +----------+  +----------+       |
              |  +----------+  +----------+  +----------+       |
              |  |FastAPI   |  |MQTT      |  |Grafana   |       |
              |  |Gateway   |  |Mosquitto |  |Monitoring|       |
              |  +----------+  +----------+  +----------+       |
              |  +----------+  +----------+                     |
              |  |MinIO     |  |Flutter   |                     |
              |  |Storage   |  |App Server|                     |
              |  +----------+  +----------+                     |
              +--------|-----------------------------------+----+
                       | WiFi / Ethernet
                       |
         +-------------+----------------+
         |     FOFOCA ROBOT (RPi5)      |
         |                              |
         |  +--------+  +--------+     |
         |  |Vision  |  |Audio   |     |
         |  |OpenCV  |  |Whisper |     |
         |  |YOLO    |  |Piper   |     |
         |  +--------+  +--------+     |
         |  +--------+  +--------+     |
         |  |ROS2    |  |Safety  |     |
         |  |Nav2    |  |Monitor |     |
         |  |SLAM    |  |Module  |     |
         |  +--------+  +--------+     |
         |                              |
         +--+-----+-----+-----+-----+--+
            |     |     |     |     |
         +--+--+--+--+--+--+--+--+--+--+
         |RPi0 |ESP32|Pico |Mega |Uno  |
         |Audio|Motor|Arm  |Sens |Aux  |
         +-----+-----+-----+-----+-----+
            |     |     |     |     |
         [Mic] [Tracks][Servos][Sensors][OLED]
         [Spk]        [Gripper]
```

### Governance Flow

1. **Sensor Data** flows from hardware to RPi5
2. **RPi5** processes locally (vision, audio, navigation)
3. **Decisions** requiring reasoning go to Local Server or ThinkNEO Cloud
4. **ThinkNEO Control Plane** applies governance policies before any action
5. **Commands** flow back through the chain: ThinkNEO -> Server -> RPi5 -> Microcontrollers -> Actuators
6. **Every action** is logged and auditable through ThinkNEO observability

---

## Power Distribution

| Rail | Source | Voltage | Max Current | Consumers |
|---|---|---|---|---|
| MAIN | Zircon Battery | 12V | 6A | Motor Driver, Buck Converters |
| RAIL_5V_A | LM2596 #1 | 5V | 3A | Raspberry Pi 5 |
| RAIL_5V_B | LM2596 #2 | 5V | 2A | Raspberry Pi Zero 2 W, USB Mic |
| RAIL_5V_C | LM2596 #3 | 5V | 2A | Servos (MG90S x6 + Gripper) |
| RAIL_5V_D | LM2596 #4 | 5V | 1A | ESP32, Arduino Uno R4 |
| RAIL_3V3 | LM2596 #5 | 3.3V | 1A | ESP8266, SIM800L |
| RAIL_VIN | Direct 12V | 12V | 2A | Arduino Mega (Vin), Motor Driver |

**Total estimated consumption:** 8-12W idle, 25-35W peak

See [docs/power-system.md](docs/power-system.md) for the full power design.

---

## 13-Phase Roadmap

| Phase | Name | Description | Status |
|---|---|---|---|
| 1 | Foundation | RPi5 setup, basic OS, network config | Complete |
| 2 | Chassis | Tank track assembly, motor driver wiring | Complete |
| 3 | Power | Battery, buck converters, power distribution | Complete |
| 4 | Locomotion | ESP32 motor control, basic movement | In Progress |
| 5 | Arm | RP2040 servo control, gripper calibration | In Progress |
| 6 | Vision | Insta360 integration, OpenCV, YOLOv8n | Planned |
| 7 | Audio | Mic array, faster-whisper, Piper TTS | Planned |
| 8 | Navigation | ROS2, SLAM mapping, autonomous pathfinding | Planned |
| 9 | Local AI | Nemotron Nano via Ollama on local server | Planned |
| 10 | ThinkNEO | Full governance integration, policy enforcement | Planned |
| 11 | Modules | Dog monitor, delivery, security, emergency | Planned |
| 12 | Mobile App | Flutter control app with live camera feed | Planned |
| 13 | Hardening | 24/7 reliability, failsafes, power management | Planned |

---

## Task Modules

FOFOCA operates through specialized task modules, each governed by ThinkNEO policies:

### Dog Monitoring
- Track pet location via YOLOv8 object detection
- Detect barking patterns via YAMNet sound classification
- Alert on unusual behavior (excessive barking, distress)
- Log feeding times and activity levels
- Navigate to pet location on command

### Delivery Reception
- Detect doorbell/knock via audio pipeline
- Navigate to entrance
- Identify delivery person via face recognition
- Extend gripper for package reception
- Log delivery with photo evidence
- Navigate to designated drop-off point

### Home Assistant
- Voice-activated commands via wake word detection
- Answer questions using Nemotron Ultra via ThinkNEO
- Control smart home devices via MQTT
- Provide weather, calendar, and reminder services
- Play music and podcasts via Bluetooth speaker

### Security Patrol
- Scheduled autonomous patrol routes via ROS2 Nav2
- Anomaly detection (open doors, unusual objects, broken windows)
- Night mode with enhanced audio monitoring
- Intrusion detection with immediate alert
- Photo/video evidence capture and storage in MinIO

### Emergency Response

| Emergency | Number | Robot Action |
|---|---|---|
| Medical (SAMU) | **192** | Detect fall/distress, call 192 via SIM800L, provide location |
| Fire | **193** | Detect smoke/heat anomaly, call 193, guide evacuation path |
| Police | **190** | Detect intrusion, call 190, record evidence, lock doors via MQTT |

All emergency protocols include:
- Automatic activation (no human command needed)
- ThinkNEO audit trail of the entire event
- GPS/address transmission to emergency services
- Continuous status updates via GSM fallback

---

## ThinkNEO Integration

FOFOCA communicates with ThinkNEO through a standard OpenAI-compatible API gateway. Every request is governed, logged, and auditable.

```python
from openai import OpenAI
import os

# ThinkNEO Gateway — governed inference
client = OpenAI(
    api_key=os.getenv("THINKNEO_KEY"),
    base_url="https://gateway.thinkneo.ai/v1"
)

def ask_fofoca(prompt: str, context: dict) -> str:
    """Send a governed inference request through ThinkNEO."""
    response = client.chat.completions.create(
        model="nvidia/llama-3.1-nemotron-ultra-253b-v1",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are FOFOCA, an autonomous household robot. "
                    "You make decisions about home tasks, pet care, "
                    "security, and emergency response. "
                    "Always prioritize safety. Always explain your reasoning."
                )
            },
            {
                "role": "user",
                "content": f"Context: {context}\n\nTask: {prompt}"
            }
        ],
        temperature=0.3,
        max_tokens=1024
    )
    return response.choices[0].message.content
```

See [src/thinkneo_integration.py](src/thinkneo_integration.py) for the full integration module.

---

## Project Structure

```
fofoca/
├── README.md                    # This file
├── LICENSE                      # MIT License
├── docs/
│   ├── architecture.md          # Detailed architecture document
│   ├── bill-of-materials.md     # Complete BOM with links
│   ├── power-system.md          # Power distribution design
│   └── software-stack.md        # Software components and config
├── src/
│   ├── thinkneo_integration.py  # ThinkNEO API integration
│   ├── emergency_module.py      # Emergency detection & response
│   ├── dog_monitor.py           # Dog monitoring module
│   └── delivery_intake.py       # Delivery reception module
└── hardware/
    └── pinout.md                # GPIO pinout reference
```

---

## Getting Started

### Prerequisites

- Raspberry Pi 5 with Raspberry Pi OS (64-bit)
- Local server running Ubuntu 24.04 LTS
- ThinkNEO account with API key ([sign up at thinkneo.ai](https://thinkneo.ai))
- Python 3.11+
- Docker and Docker Compose

### Quick Start

```bash
# Clone the repository
git clone https://github.com/thinkneo-ai/fofoca.git
cd fofoca

# Install Python dependencies (on RPi5)
pip install openai fastapi paho-mqtt opencv-python ultralytics

# Set your ThinkNEO API key
export THINKNEO_KEY="your-api-key-here"

# Test the ThinkNEO connection
python src/thinkneo_integration.py
```

---

## Contributing

FOFOCA is an open study case and contributions are welcome. Whether you want to improve the hardware design, add new task modules, enhance the AI pipeline, or improve documentation — we'd love your help.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## Links

- **Live Site:** [thinkneorobotics.online](https://thinkneorobotics.online)
- **ThinkNEO Platform:** [thinkneo.ai](https://thinkneo.ai)
- **NVIDIA Inception:** [nvidia.com/inception](https://www.nvidia.com/en-us/startups/)

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  <br />
  <strong>Built with governance by <a href="https://thinkneo.ai">ThinkNEO</a></strong>
  <br />
  <em>Enterprise AI Control Plane</em>
  <br />
  <br />
  <img src="https://img.shields.io/badge/Powered%20by-NVIDIA-76B900?style=flat-square&logo=nvidia&logoColor=white" alt="Powered by NVIDIA" />
  <img src="https://img.shields.io/badge/Governed%20by-ThinkNEO-blueviolet?style=flat-square" alt="Governed by ThinkNEO" />
</p>
