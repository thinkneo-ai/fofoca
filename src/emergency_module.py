"""
FOFOCA — Emergency Detection & Response Module

Monitors sensor data for emergency conditions and triggers appropriate
responses including automated calls to Brazilian emergency services.

Emergency Numbers:
    - SAMU (Medical): 192
    - Fire Department: 193
    - Police: 190

All emergency actions are governed by ThinkNEO and logged to the audit trail.
"""

import os
import json
import logging
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

logger = logging.getLogger("fofoca.emergency")


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------


class EmergencyType(Enum):
    MEDICAL = "medical"
    FIRE = "fire"
    INTRUSION = "intrusion"
    FALL_DETECTED = "fall_detected"
    GAS_LEAK = "gas_leak"
    UNKNOWN = "unknown"


class Severity(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    LIFE_THREATENING = 5


EMERGENCY_NUMBERS = {
    EmergencyType.MEDICAL: "192",       # SAMU
    EmergencyType.FALL_DETECTED: "192", # SAMU
    EmergencyType.FIRE: "193",          # Bombeiros
    EmergencyType.GAS_LEAK: "193",      # Bombeiros
    EmergencyType.INTRUSION: "190",     # Policia
}


@dataclass
class EmergencyEvent:
    """Represents a detected emergency event."""
    event_type: EmergencyType
    severity: Severity
    confidence: float
    source: str  # sensor that triggered
    description: str
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    location: Optional[str] = None
    sensor_data: Optional[dict] = None
    resolved: bool = False
    resolution: Optional[str] = None


# ---------------------------------------------------------------------------
# Emergency Detector
# ---------------------------------------------------------------------------


class EmergencyDetector:
    """
    Monitors sensor inputs and detects emergency conditions.

    This is a skeleton implementation. In production, each detect_*
    method would be connected to real sensor feeds via MQTT.
    """

    def __init__(self, thinkneo_brain=None, mqtt_client=None, gsm_port=None):
        """
        Args:
            thinkneo_brain: FofocaBrain instance for governed decision-making.
            mqtt_client: Paho MQTT client for sensor data subscription.
            gsm_port: Serial port for SIM800L GSM module (e.g., /dev/ttyUSB1).
        """
        self.brain = thinkneo_brain
        self.mqtt = mqtt_client
        self.gsm_port = gsm_port or os.getenv("GSM_PORT", "/dev/ttyUSB1")
        self.active_emergencies: list[EmergencyEvent] = []
        self.emergency_contacts = os.getenv(
            "EMERGENCY_CONTACTS", ""
        ).split(",")

        logger.info("EmergencyDetector initialized — GSM port: %s", self.gsm_port)

    # ------------------------------------------------------------------
    # Detection methods (skeleton — connect to real sensors)
    # ------------------------------------------------------------------

    def detect_fall(self, vision_data: dict) -> Optional[EmergencyEvent]:
        """
        Detect a person falling using vision pipeline data.

        In production: analyzes pose estimation data from YOLOv8-pose
        to detect sudden transitions from standing to lying position.
        """
        # Skeleton: check for person detected in lying position
        for detection in vision_data.get("detections", []):
            if (
                detection.get("class") == "person"
                and detection.get("pose") == "lying"
                and detection.get("confidence", 0) > 0.8
            ):
                return EmergencyEvent(
                    event_type=EmergencyType.FALL_DETECTED,
                    severity=Severity.CRITICAL,
                    confidence=detection["confidence"],
                    source="vision_yolov8_pose",
                    description="Person detected in lying position — possible fall",
                    location=vision_data.get("room", "unknown"),
                    sensor_data=detection,
                )
        return None

    def detect_fire(self, sensor_data: dict) -> Optional[EmergencyEvent]:
        """
        Detect fire conditions using audio and environmental sensors.

        In production: combines YAMNet smoke alarm detection,
        temperature sensors, and gas sensors.
        """
        smoke_alarm = sensor_data.get("audio_event") == "smoke_alarm"
        high_temp = sensor_data.get("temperature", 0) > 50
        gas_detected = sensor_data.get("gas_level", 0) > 800  # ppm

        if smoke_alarm or (high_temp and gas_detected):
            return EmergencyEvent(
                event_type=EmergencyType.FIRE,
                severity=Severity.LIFE_THREATENING,
                confidence=0.9 if smoke_alarm else 0.7,
                source="multi_sensor_fusion",
                description="Fire conditions detected — smoke alarm and/or high temperature",
                sensor_data=sensor_data,
            )
        return None

    def detect_intrusion(self, sensor_data: dict) -> Optional[EmergencyEvent]:
        """
        Detect unauthorized entry using vision and door sensors.

        In production: combines face recognition (unknown face),
        door/window sensors, and time-of-day context.
        """
        unknown_person = sensor_data.get("unknown_face_detected", False)
        door_forced = sensor_data.get("door_sensor") == "forced_open"
        night_time = sensor_data.get("is_night", False)

        if unknown_person and (door_forced or night_time):
            return EmergencyEvent(
                event_type=EmergencyType.INTRUSION,
                severity=Severity.HIGH,
                confidence=0.85,
                source="vision_door_sensor",
                description="Possible intrusion — unknown person detected",
                sensor_data=sensor_data,
            )
        return None

    def detect_gas_leak(self, sensor_data: dict) -> Optional[EmergencyEvent]:
        """
        Detect gas leak using environmental sensors.

        In production: reads MQ-2 or MQ-5 gas sensor via Arduino Mega.
        """
        gas_level = sensor_data.get("gas_level", 0)
        if gas_level > 1000:  # ppm — dangerous level
            return EmergencyEvent(
                event_type=EmergencyType.GAS_LEAK,
                severity=Severity.LIFE_THREATENING,
                confidence=0.95,
                source="gas_sensor_mq2",
                description=f"Gas leak detected — {gas_level} ppm",
                sensor_data=sensor_data,
            )
        return None

    # ------------------------------------------------------------------
    # Response actions
    # ------------------------------------------------------------------

    def handle_emergency(self, event: EmergencyEvent) -> dict:
        """
        Handle a detected emergency event.

        Steps:
        1. Consult ThinkNEO for governed decision
        2. Sound local alarm
        3. Call emergency services via GSM if severity >= CRITICAL
        4. Notify emergency contacts
        5. Log everything to audit trail

        Returns:
            Dictionary with actions_taken and ThinkNEO assessment.
        """
        logger.critical(
            "EMERGENCY DETECTED — type=%s, severity=%s, confidence=%.2f",
            event.event_type.value,
            event.severity.value,
            event.confidence,
        )

        self.active_emergencies.append(event)
        actions_taken = []

        # Step 1: Consult ThinkNEO (if available)
        assessment = None
        if self.brain:
            try:
                assessment = self.brain.assess_emergency(asdict(event))
                logger.info("ThinkNEO assessment: %s", assessment)
            except Exception as e:
                logger.error("ThinkNEO unavailable during emergency: %s", e)
                # Proceed with local decision-making
                assessment = {"action": "proceed_locally", "reasoning": str(e)}

        # Step 2: Sound local alarm
        self._sound_alarm(event)
        actions_taken.append("alarm_sounded")

        # Step 3: Call emergency services if critical
        if event.severity.value >= Severity.CRITICAL.value:
            number = EMERGENCY_NUMBERS.get(event.event_type)
            if number:
                self._call_emergency_number(number, event)
                actions_taken.append(f"called_{number}")

        # Step 4: Notify emergency contacts
        self._notify_contacts(event)
        actions_taken.append("contacts_notified")

        # Step 5: Log to audit trail
        audit_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": asdict(event),
            "assessment": assessment,
            "actions_taken": actions_taken,
        }
        self._log_audit(audit_entry)
        actions_taken.append("audit_logged")

        return {
            "actions_taken": actions_taken,
            "assessment": assessment,
            "emergency_number_called": EMERGENCY_NUMBERS.get(event.event_type),
        }

    # ------------------------------------------------------------------
    # Private methods (skeleton implementations)
    # ------------------------------------------------------------------

    def _sound_alarm(self, event: EmergencyEvent):
        """Sound the local alarm via Arduino buzzer and Bluetooth speaker."""
        logger.info("Sounding alarm for %s", event.event_type.value)
        if self.mqtt:
            self.mqtt.publish(
                "fofoca/command/alarm",
                json.dumps({
                    "type": event.event_type.value,
                    "severity": event.severity.value,
                }),
            )

    def _call_emergency_number(self, number: str, event: EmergencyEvent):
        """
        Call an emergency number via SIM800L GSM module.

        In production: sends AT commands to SIM800L via serial port.
        """
        logger.critical("CALLING EMERGENCY NUMBER: %s", number)
        # Skeleton: In production, this sends AT commands:
        # AT+CMGF=1        (SMS text mode)
        # ATD192;           (dial SAMU)
        # etc.
        pass

    def _notify_contacts(self, event: EmergencyEvent):
        """Send SMS to emergency contacts via SIM800L."""
        message = (
            f"FOFOCA EMERGENCY: {event.event_type.value} detected. "
            f"Severity: {event.severity.value}/5. "
            f"Location: {event.location or 'unknown'}. "
            f"Time: {event.timestamp}"
        )
        logger.info("Notifying %d contacts", len(self.emergency_contacts))
        for contact in self.emergency_contacts:
            if contact.strip():
                logger.info("SMS to %s: %s", contact, message)
                # Skeleton: send via SIM800L AT+CMGS command

    def _log_audit(self, entry: dict):
        """Log emergency event to audit trail."""
        logger.info("Audit trail: %s", json.dumps(entry, default=str))
        # In production: POST to ThinkNEO audit endpoint
        # and save locally to PostgreSQL


# ---------------------------------------------------------------------------
# Standalone test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    detector = EmergencyDetector()

    # Simulate a fall detection
    test_vision_data = {
        "room": "living_room",
        "detections": [
            {
                "class": "person",
                "pose": "lying",
                "confidence": 0.92,
                "bbox": [100, 300, 400, 500],
            }
        ],
    }

    event = detector.detect_fall(test_vision_data)
    if event:
        result = detector.handle_emergency(event)
        print(f"\nEmergency handled: {json.dumps(result, indent=2)}")
    else:
        print("No emergency detected.")
