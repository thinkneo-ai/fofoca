# FOFOCA Bill of Materials

> Complete bill of materials with specifications, quantities, and estimated prices.

---

## Compute & Control

| # | Component | Specs | Role | Qty | Est. Price | Notes |
|---|---|---|---|---|---|---|
| 1 | Raspberry Pi 5 | 8GB RAM, BCM2712, USB3, PCIe | Main brain | 1 | $80 | Requires active cooler |
| 2 | Raspberry Pi Zero 2 W | 512MB RAM, BCM2710A1, WiFi/BT | Audio co-processor | 1 | $15 | Header soldering needed |
| 3 | RP2040 Pico | Dual ARM Cortex-M0+, 264KB SRAM | Arm PWM controller | 1 | $4 | No WiFi variant |
| 4 | ESP32 DevKit V1 | 240MHz, 520KB SRAM, WiFi+BT | Motor control, sensors | 1 | $8 | WROOM-32 module |
| 5 | Arduino Mega 2560 | ATmega2560, 54 digital I/O, 16 analog | Sensor hub | 1 | $15 | Clone acceptable |
| 6 | Arduino Uno R4 WiFi | RA4M1 + ESP32-S3, USB-C | Aux interface | 1 | $27 | Built-in WiFi |

**Subtotal: ~$149**

---

## Sensors & Perception

| # | Component | Specs | Role | Qty | Est. Price | Notes |
|---|---|---|---|---|---|---|
| 7 | Insta360 X3 or X4 | 5.7K 360°, USB-C, Live preview | Panoramic vision | 1 | $300-450 | USB webcam mode |
| 8 | ReSpeaker USB Mic Array | 4-mic circular, far-field | Voice capture | 1 | $30 | Seeed Studio |
| 9 | ESP8266 + 0.96" OLED | I2C SSD1306, 128x64px | Status display | 1 | $6 | NodeMCU variant |
| 10 | Keystudio IO Expander v5.0 | Multiple I/O ports, easy connect | GPIO expansion | 1 | $12 | Keystudio brand |

**Subtotal: ~$348-498**

---

## Locomotion & Actuators

| # | Component | Specs | Role | Qty | Est. Price | Notes |
|---|---|---|---|---|---|---|
| 11 | MG90S Micro Servo | Metal gear, 1.8kg/cm, 180° | Arm joints | 6 | $18 | $3 each |
| 12 | Robot Gripper Kit | Dual-finger, servo-driven | End effector | 1 | $8 | Compatible with MG90S |
| 13 | Tank Track Chassis Kit | Aluminum/plastic, dual motor | Tracked locomotion | 1 | $35 | Includes DC motors |
| 14 | HW130 Motor Driver | Dual H-bridge, 1.5A per ch | DC motor driver | 1 | $5 | L9110S based |
| 15 | Microstep Driver | A4988 or DRV8825 | Arm base stepper | 1 | $4 | With heatsink |
| 16 | Bluetooth Speaker | 3W, rechargeable, 3.5mm | Audio output | 1 | $10 | BT 5.0 preferred |

**Subtotal: ~$80**

---

## Power System

| # | Component | Specs | Role | Qty | Est. Price | Notes |
|---|---|---|---|---|---|---|
| 17 | Zircon 12V LiFePO4 Battery | 6Ah+, 72Wh, >500 cycles | Main battery | 1 | $45 | LiFePO4 for safety |
| 18 | LM2596 Buck Converter | Adjustable 1.25-35V, 3A | Voltage regulation | 5 | $5 | $1 each, pre-set |
| 19 | SIM800L GSM Module | Quad-band, SMS, voice calls | Cellular fallback | 1 | $8 | Needs 2G coverage |

**Subtotal: ~$58**

---

## Cables, Connectors & Misc

| # | Component | Role | Qty | Est. Price |
|---|---|---|---|---|
| 20 | Dupont jumper wires (M-M, M-F, F-F) | Interconnect | 3 packs | $6 |
| 21 | Breadboard 830-point | Prototyping | 2 | $4 |
| 22 | PCB prototype board | Permanent circuits | 3 | $3 |
| 23 | USB-C cables (30cm, 1m) | RPi5 power and data | 3 | $6 |
| 24 | Micro USB cables | ESP32, Arduino power | 3 | $3 |
| 25 | XT60 connectors | Battery main power | 2 pairs | $3 |
| 26 | Barrel jack connectors (5.5x2.1mm) | Buck converter output | 5 | $3 |
| 27 | Heat shrink tubing kit | Wire insulation | 1 kit | $3 |
| 28 | M3 standoff kit | Board mounting | 1 kit | $5 |
| 29 | Zip ties + Velcro straps | Cable management | 1 pack | $3 |
| 30 | 3D printed chassis parts | Custom mounting brackets | Various | $10-20 |

**Subtotal: ~$49-59**

---

## Local Server (Separate from Robot)

| # | Component | Specs | Role | Est. Price |
|---|---|---|---|---|
| 31 | PC / Gaming PC | 16GB+ RAM, any modern CPU | Local inference server | Varies |
| 32 | GPU (optional) | NVIDIA GTX 1060+ or RTX | Accelerated inference | Varies |
| 33 | Ubuntu Server 24.04 LTS | 64-bit, headless | Operating system | Free |

**Note:** Any reasonably modern PC works. A dedicated GPU significantly improves local Nemotron Nano inference speed but is not required — CPU inference is functional.

---

## Total Cost Summary

| Category | Min. Est. | Max. Est. |
|---|---|---|
| Compute & Control | $149 | $149 |
| Sensors & Perception | $348 | $498 |
| Locomotion & Actuators | $80 | $80 |
| Power System | $58 | $58 |
| Cables & Misc | $49 | $59 |
| **Total (Robot Only)** | **$684** | **$844** |
| Local Server PC | Varies | Varies |

**Without Insta360 camera (using a standard USB webcam instead): ~$384-394**

---

## Where to Buy

Most components are available from:

- **Raspberry Pi:** [raspberrypi.com](https://www.raspberrypi.com/) or local distributors
- **Arduino / ESP32:** [arduino.cc](https://store.arduino.cc/), AliExpress, Amazon
- **Insta360:** [insta360.com](https://www.insta360.com/)
- **Seeed Studio (ReSpeaker):** [seeedstudio.com](https://www.seeedstudio.com/)
- **Generic components:** AliExpress, Amazon, local electronics shops

---

*Part of the [FOFOCA](https://github.com/thinkneo-ai/fofoca) open study case by [ThinkNEO](https://thinkneo.ai).*
