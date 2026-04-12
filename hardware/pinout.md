# FOFOCA GPIO Pinout Reference

> Raspberry Pi 5 GPIO connections to all peripherals and microcontrollers.

---

## Raspberry Pi 5 — 40-Pin Header

```
                    +-----+-----+
           3V3  1  | o   o |  2   5V
    I2C1 SDA  3  | o   o |  4   5V
    I2C1 SCL  5  | o   o |  6   GND
     (free)   7  | o   o |  8   UART TX (-> ESP32 RX)
          GND  9  | o   o | 10   UART RX (<- ESP32 TX)
  ESP32 RST  11  | o   o | 12   (free)
     (free)  13  | o   o | 14   GND
     (free)  15  | o   o | 16   PICO SDA (I2C0)
           3V3  17  | o   o | 18   PICO SCL (I2C0)
   SPI MOSI  19  | o   o | 20   GND
   SPI MISO  21  | o   o | 22   E-STOP (input, pull-up)
   SPI SCLK  23  | o   o | 24   SPI CE0 (Mega CS)
          GND  25  | o   o | 26   SPI CE1 (reserved)
  EEPROM SDA  27  | o   o | 28   EEPROM SCL
     (free)  29  | o   o | 30   GND
  HEARTBEAT  31  | o   o | 32   BATTERY_ADC (from ESP32)
     (free)  33  | o   o | 34   GND
     (free)  35  | o   o | 36   STATUS_LED
     (free)  37  | o   o | 38   (free)
          GND  39  | o   o | 40   (free)
                    +-----+-----+
```

---

## Connection Map

### UART (Serial) — RPi5 <-> ESP32

| RPi5 Pin | GPIO | Function | Connected To |
|---|---|---|---|
| Pin 8 | GPIO 14 | UART TX | ESP32 GPIO 16 (RX2) |
| Pin 10 | GPIO 15 | UART RX | ESP32 GPIO 17 (TX2) |
| Pin 6 | GND | Ground | ESP32 GND |

**Baud rate:** 115200
**Protocol:** Custom JSON messages over serial

```
RPi5 TX (Pin 8) -------> ESP32 RX2 (GPIO 16)
RPi5 RX (Pin 10) <------ ESP32 TX2 (GPIO 17)
RPi5 GND (Pin 6) ------- ESP32 GND
```

### I2C Bus 1 — RPi5 <-> Arduino Mega

| RPi5 Pin | GPIO | Function | Connected To |
|---|---|---|---|
| Pin 3 | GPIO 2 | I2C1 SDA | Arduino Mega SDA (Pin 20) |
| Pin 5 | GPIO 3 | I2C1 SCL | Arduino Mega SCL (Pin 21) |
| Pin 9 | GND | Ground | Arduino Mega GND |

**I2C Address:** 0x08 (Mega as slave)
**Speed:** 400 kHz (Fast Mode)

### I2C Bus 0 — RPi5 <-> RP2040 Pico

| RPi5 Pin | GPIO | Function | Connected To |
|---|---|---|---|
| Pin 16 | GPIO 23 | I2C0 SDA | Pico GP4 (SDA) |
| Pin 18 | GPIO 24 | I2C0 SCL | Pico GP5 (SCL) |
| Pin 20 | GND | Ground | Pico GND |

**I2C Address:** 0x10 (Pico as slave)
**Speed:** 400 kHz (Fast Mode)

### SPI — RPi5 <-> Arduino Mega (High-Speed Sensor Data)

| RPi5 Pin | GPIO | Function | Connected To |
|---|---|---|---|
| Pin 19 | GPIO 10 | SPI MOSI | Mega MOSI (Pin 51) |
| Pin 21 | GPIO 9 | SPI MISO | Mega MISO (Pin 50) |
| Pin 23 | GPIO 11 | SPI SCLK | Mega SCK (Pin 52) |
| Pin 24 | GPIO 8 | SPI CE0 | Mega SS (Pin 53) |
| Pin 25 | GND | Ground | Mega GND |

**Speed:** 1 MHz
**Mode:** SPI Mode 0

### USB Connections

| RPi5 Port | Device | Protocol |
|---|---|---|
| USB 3.0 #1 | Insta360 X3/X4 | USB Video Class (UVC) |
| USB 3.0 #2 | ReSpeaker Mic Array | USB Audio Class (UAC) |
| USB 2.0 #1 | Arduino Uno R4 WiFi | CDC Serial |
| USB 2.0 #2 | SIM800L (via USB-Serial) | AT Commands |

### Digital GPIO — Miscellaneous

| RPi5 Pin | GPIO | Function | Direction | Notes |
|---|---|---|---|---|
| Pin 11 | GPIO 17 | ESP32 Reset | Output | Pull low to reset ESP32 |
| Pin 22 | GPIO 25 | Emergency Stop | Input | Active low, external pull-up |
| Pin 31 | GPIO 6 | Heartbeat Out | Output | 1Hz pulse to ESP32 watchdog |
| Pin 32 | GPIO 12 | Battery ADC | Input | Analog read via ESP32 ADC |
| Pin 36 | GPIO 16 | Status LED | Output | Green = OK, Blink = Busy |

---

## ESP32 DevKit V1 — Pin Assignments

| ESP32 Pin | Function | Connected To |
|---|---|---|
| GPIO 16 (RX2) | UART RX from RPi5 | RPi5 Pin 8 (TX) |
| GPIO 17 (TX2) | UART TX to RPi5 | RPi5 Pin 10 (RX) |
| GPIO 25 | Motor A PWM (Left Track) | HW130 IN1 |
| GPIO 26 | Motor A DIR (Left Track) | HW130 IN2 |
| GPIO 27 | Motor B PWM (Right Track) | HW130 IN3 |
| GPIO 14 | Motor B DIR (Right Track) | HW130 IN4 |
| GPIO 34 | Battery Voltage (ADC) | Voltage divider from 12V |
| GPIO 35 | Ultrasonic Echo (Front) | HC-SR04 Echo |
| GPIO 32 | Ultrasonic Trigger (Front) | HC-SR04 Trigger |
| GPIO 33 | Ultrasonic Echo (Rear) | HC-SR04 Echo |
| GPIO 4 | Ultrasonic Trigger (Rear) | HC-SR04 Trigger |
| GPIO 5 | Heartbeat Input | RPi5 Pin 31 (GPIO 6) |
| EN | Reset | RPi5 Pin 11 (GPIO 17) |

---

## RP2040 Pico — Pin Assignments

| Pico Pin | Function | Connected To |
|---|---|---|
| GP4 (SDA) | I2C SDA | RPi5 Pin 16 (I2C0 SDA) |
| GP5 (SCL) | I2C SCL | RPi5 Pin 18 (I2C0 SCL) |
| GP0 | Servo 1 PWM (Base Rotate) | MG90S #1 Signal |
| GP1 | Servo 2 PWM (Shoulder) | MG90S #2 Signal |
| GP2 | Servo 3 PWM (Elbow) | MG90S #3 Signal |
| GP3 | Servo 4 PWM (Wrist Pitch) | MG90S #4 Signal |
| GP6 | Servo 5 PWM (Wrist Roll) | MG90S #5 Signal |
| GP7 | Servo 6 PWM (Wrist Yaw) | MG90S #6 Signal |
| GP8 | Gripper PWM | Gripper Servo Signal |
| GND | Ground | Common GND |
| VSYS | 5V Power | RAIL_5V_C |

**PWM Frequency:** 50 Hz (standard servo)
**Pulse Range:** 500us (0°) to 2500us (180°)

---

## Arduino Mega 2560 — Sensor Hub Pin Assignments

| Mega Pin | Function | Sensor |
|---|---|---|
| A0 | Temperature (analog) | LM35 / TMP36 |
| A1 | Humidity (analog) | Analog humidity sensor |
| A2 | Gas Level (analog) | MQ-2 Gas Sensor |
| A3 | Light Level (analog) | LDR photoresistor |
| A4 | Spare Analog | Reserved |
| A5 | Spare Analog | Reserved |
| D2 | PIR Motion (interrupt) | HC-SR501 PIR |
| D3 | Door Sensor (interrupt) | Magnetic reed switch |
| D4 | Window Sensor 1 | Magnetic reed switch |
| D5 | Window Sensor 2 | Magnetic reed switch |
| D20 (SDA) | I2C SDA to RPi5 | RPi5 Pin 3 (I2C1) |
| D21 (SCL) | I2C SCL to RPi5 | RPi5 Pin 5 (I2C1) |
| D50 (MISO) | SPI MISO | RPi5 Pin 21 |
| D51 (MOSI) | SPI MOSI | RPi5 Pin 19 |
| D52 (SCK) | SPI SCLK | RPi5 Pin 23 |
| D53 (SS) | SPI Slave Select | RPi5 Pin 24 |

---

## Arduino Uno R4 WiFi — Aux Interface Pin Assignments

| Uno R4 Pin | Function | Component |
|---|---|---|
| D2 | Button 1 (Manual Override) | Momentary push button |
| D3 | Button 2 (Emergency Stop) | Latching push button |
| D5 | Buzzer PWM | Piezo buzzer |
| D9 | RGB LED Red | Common cathode RGB LED |
| D10 | RGB LED Green | Common cathode RGB LED |
| D11 | RGB LED Blue | Common cathode RGB LED |
| USB | Serial to RPi5 | USB 2.0 CDC |

---

## Wiring Safety Notes

1. **ALWAYS** connect GND between all boards before connecting signal wires
2. **NEVER** connect 5V logic directly to 3.3V devices — use level shifters
3. **ALWAYS** add 100nF decoupling capacitors near each MCU power pin
4. **ALWAYS** use pull-up resistors (4.7K) on I2C lines
5. **NEVER** exceed 16mA per GPIO pin on RPi5
6. **ALWAYS** use flyback diodes on motor driver outputs
7. **ALWAYS** fuse the main battery output (10A automotive fuse)

---

*Part of the [FOFOCA](https://github.com/thinkneo-ai/fofoca) open study case by [ThinkNEO](https://thinkneo.ai).*
