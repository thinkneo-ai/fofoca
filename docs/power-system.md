# FOFOCA Power System Design

> Detailed power distribution design for the FOFOCA autonomous household robot.

---

## Overview

FOFOCA runs on a single **Zircon 12V 6Ah+ LiFePO4 battery** that powers the entire robot through a regulated power distribution network. Five LM2596 buck converters step down the 12V main rail to the voltages required by each subsystem.

LiFePO4 chemistry was chosen for:
- **Safety** — no thermal runaway risk (critical for a household robot)
- **Longevity** — 2000+ cycle life vs. 500 for standard Li-ion
- **Flat discharge curve** — stable voltage throughout discharge
- **Operating temperature** — safe from -20C to 60C

---

## Power Distribution Diagram

```
                    ┌─────────────────────────┐
                    │  Zircon 12V 6Ah LiFePO4 │
                    │  72Wh  │  XT60 Output    │
                    └────────┬────────────────┘
                             │ 12V Main Rail
                             │
              ┌──────────────┼──────────────────┐
              │              │                   │
              │         ┌────┴────┐              │
              │         │ Fuse 10A│              │
              │         └────┬────┘              │
              │              │                   │
    ┌─────────┼──────────────┼───────────────────┼─────────────┐
    │         │              │                   │             │
┌───┴───┐ ┌──┴───┐    ┌────┴────┐         ┌───┴───┐   ┌────┴────┐
│LM2596 │ │LM2596│    │ LM2596  │         │LM2596 │   │ LM2596  │
│  #1   │ │  #2  │    │   #3    │         │  #4   │   │   #5    │
│ 5V 3A │ │5V 2A │    │ 5V 2A  │         │5V 1A  │   │3.3V 1A │
└───┬───┘ └──┬───┘    └───┬────┘         └───┬───┘   └────┬────┘
    │        │             │                  │             │
    │        │             │                  │             │
┌───┴───┐┌──┴────┐  ┌────┴─────┐      ┌───┴────┐   ┌────┴─────┐
│ RPi 5 ││RPi 0  │  │ Servos   │      │ ESP32  │   │ ESP8266  │
│       ││+ Mic  │  │ MG90S x6 │      │+ Uno R4│   │+ SIM800L │
│ 2.5A  ││ 0.8A  │  │ Gripper  │      │  0.5A  │   │  0.5A    │
└───────┘└───────┘  │  1.5A pk │      └────────┘   └──────────┘
                    └──────────┘

              Direct 12V Rail (no regulator)
              ┌─────────────────────────────┐
              │                             │
         ┌────┴─────┐              ┌───────┴────────┐
         │ Arduino  │              │  HW130 Motor   │
         │ Mega 2560│              │  Driver        │
         │ (Vin pin)│              │  Track Motors  │
         │  0.2A    │              │  2A peak       │
         └──────────┘              └────────────────┘
```

---

## Rail Specifications

### RAIL_5V_A — Raspberry Pi 5

| Parameter | Value |
|---|---|
| Source | LM2596 #1 |
| Output Voltage | 5.1V (tuned) |
| Max Current | 3A |
| Typical Load | 1.5-2.5A |
| Consumer | Raspberry Pi 5 (USB-C PD) |
| Notes | Requires stable 5.1V; drooping below 4.9V triggers throttling |

### RAIL_5V_B — Audio Subsystem

| Parameter | Value |
|---|---|
| Source | LM2596 #2 |
| Output Voltage | 5.0V |
| Max Current | 2A |
| Typical Load | 0.3-0.8A |
| Consumers | Raspberry Pi Zero 2 W, ReSpeaker USB Mic |
| Notes | Separate rail to avoid audio noise from RPi5 |

### RAIL_5V_C — Servo Array

| Parameter | Value |
|---|---|
| Source | LM2596 #3 |
| Output Voltage | 5.0V |
| Max Current | 2A |
| Typical Load | 0.3-1.5A (peak during movement) |
| Consumers | 6x MG90S servos + 1 gripper servo |
| Notes | Dedicated rail prevents servo current spikes from affecting logic |

### RAIL_5V_D — Microcontrollers

| Parameter | Value |
|---|---|
| Source | LM2596 #4 |
| Output Voltage | 5.0V |
| Max Current | 1A |
| Typical Load | 0.2-0.5A |
| Consumers | ESP32 DevKit, Arduino Uno R4 WiFi |
| Notes | Low-power rail for control MCUs |

### RAIL_3V3 — Low Voltage Devices

| Parameter | Value |
|---|---|
| Source | LM2596 #5 |
| Output Voltage | 3.3V |
| Max Current | 1A |
| Typical Load | 0.1-0.5A |
| Consumers | ESP8266 + OLED, SIM800L GSM |
| Notes | SIM800L has 2A peak during transmission — add 1000uF cap |

### RAIL_VIN — Direct 12V

| Parameter | Value |
|---|---|
| Source | Battery direct (fused) |
| Voltage | 10.8-13.2V (battery range) |
| Max Current | 2.5A |
| Consumers | Arduino Mega 2560 (Vin), HW130 Motor Driver |
| Notes | Motor driver handles 12V directly for track DC motors |

---

## Power Budget

### Idle State (Robot Stationary, Listening)

| Subsystem | Current (5V equiv.) | Power |
|---|---|---|
| RPi5 (idle) | 0.8A @ 5V | 4.0W |
| RPi Zero 2W (listening) | 0.2A @ 5V | 1.0W |
| ESP32 (idle) | 0.08A @ 5V | 0.4W |
| Arduino Mega (idle) | 0.05A @ 12V | 0.6W |
| Arduino Uno R4 (idle) | 0.05A @ 5V | 0.25W |
| ESP8266 + OLED | 0.08A @ 3.3V | 0.26W |
| USB Mic (active) | 0.1A @ 5V | 0.5W |
| **Total Idle** | | **~7W** |

### Active State (Moving, Processing, Talking)

| Subsystem | Current (5V equiv.) | Power |
|---|---|---|
| RPi5 (full load) | 2.5A @ 5V | 12.5W |
| RPi Zero 2W (TTS active) | 0.4A @ 5V | 2.0W |
| ESP32 (motors running) | 0.15A @ 5V | 0.75W |
| Track Motors | 1.5A @ 12V | 18.0W |
| Servos (3 moving) | 0.9A @ 5V | 4.5W |
| Arduino Mega (sensors) | 0.1A @ 12V | 1.2W |
| Arduino Uno R4 | 0.1A @ 5V | 0.5W |
| ESP8266 + OLED | 0.08A @ 3.3V | 0.26W |
| USB Mic + Speaker | 0.3A @ 5V | 1.5W |
| SIM800L (transmitting) | 2.0A @ 3.3V peak | 6.6W peak |
| **Total Active** | | **~35W** |

### Battery Life Estimates

| State | Power Draw | Battery Life (72Wh) |
|---|---|---|
| Idle (listening only) | ~7W | ~10 hours |
| Light activity (occasional movement) | ~15W | ~5 hours |
| Active patrol | ~25W | ~3 hours |
| Full active (motors + AI + comms) | ~35W | ~2 hours |

---

## Protection Features

### Over-current Protection
- 10A automotive fuse on main battery output
- Each LM2596 has built-in current limiting
- HW130 motor driver has thermal shutdown

### Voltage Monitoring
- ESP32 ADC reads battery voltage via voltage divider (100K/33K)
- Thresholds:
  - **>12.8V** — Fully charged
  - **12.0V** — Normal operation
  - **11.5V** — Low battery warning (LED + voice alert)
  - **11.0V** — Critical — navigate to charging station
  - **10.8V** — Emergency shutdown (protect battery cells)

### Reverse Polarity Protection
- Schottky diode on main power input
- All buck converters have reverse input protection

### Noise Isolation
- Servo rail is separate from logic rails (prevents brownout)
- Motor driver rail is separate from everything
- 100uF electrolytic + 100nF ceramic capacitors on each MCU power pin
- 1000uF electrolytic on SIM800L power (2A transmission spikes)

---

## Charging

The LiFePO4 battery charges via its built-in BMS (Battery Management System) using a standard 14.6V LiFePO4 charger. The robot must be powered off or in standby during charging.

**Future enhancement (Phase 13):** Autonomous docking station with charging contacts, allowing the robot to self-charge when battery is low.

---

## Wiring Color Code

| Color | Purpose |
|---|---|
| Red | Positive power (any voltage) |
| Black | Ground (GND) |
| Yellow | 12V rail |
| Orange | 5V rail |
| Blue | 3.3V rail |
| Green | Signal / data lines |
| White | I2C SDA |
| Purple | I2C SCL |
| Grey | UART TX |
| Brown | UART RX |

---

*Part of the [FOFOCA](https://github.com/thinkneo-ai/fofoca) open study case by [ThinkNEO](https://thinkneo.ai).*
