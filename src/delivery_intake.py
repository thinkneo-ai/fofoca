"""
FOFOCA — Delivery Reception Module

Handles automated delivery reception at the front door.
Uses vision (face recognition, package detection) and audio
(doorbell, knock detection) to manage the delivery workflow.

Workflow:
1. Detect doorbell ring or knock
2. Navigate to front door
3. Identify delivery person (known vs unknown)
4. Extend gripper for small packages
5. Photograph delivery as evidence
6. Transport package to designated area
7. Notify homeowner

All actions are governed by ThinkNEO and logged to the audit trail.
"""

import json
import logging
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

logger = logging.getLogger("fofoca.delivery")


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------


class DeliveryStatus(Enum):
    DETECTED = "detected"
    NAVIGATING_TO_DOOR = "navigating_to_door"
    AT_DOOR = "at_door"
    IDENTIFYING = "identifying"
    RECEIVING = "receiving"
    TRANSPORTING = "transporting"
    STORED = "stored"
    FAILED = "failed"
    COMPLETED = "completed"


class DeliveryTrigger(Enum):
    DOORBELL = "doorbell"
    KNOCK = "knock"
    PERSON_AT_DOOR = "person_at_door"
    PACKAGE_ON_GROUND = "package_on_ground"
    MANUAL = "manual"


@dataclass
class DeliveryEvent:
    """Represents a delivery reception event."""
    delivery_id: str
    trigger: DeliveryTrigger
    status: DeliveryStatus = DeliveryStatus.DETECTED
    timestamp_start: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    timestamp_end: Optional[str] = None
    person_identified: bool = False
    person_name: Optional[str] = None
    person_confidence: float = 0.0
    package_detected: bool = False
    package_size: Optional[str] = None  # small, medium, large
    photo_path: Optional[str] = None
    drop_off_location: str = "entrance_table"
    notes: list = field(default_factory=list)


# ---------------------------------------------------------------------------
# Delivery Intake Manager
# ---------------------------------------------------------------------------


class DeliveryIntake:
    """
    Manages the automated delivery reception workflow.

    This is a skeleton implementation. In production, each method
    would interface with real hardware through MQTT and the ROS2
    navigation stack.
    """

    def __init__(
        self,
        thinkneo_brain=None,
        mqtt_client=None,
        minio_client=None,
        door_location: Optional[dict] = None,
        drop_off_location: Optional[dict] = None,
    ):
        """
        Args:
            thinkneo_brain: FofocaBrain instance for governed decisions.
            mqtt_client: Paho MQTT client for robot commands.
            minio_client: MinIO client for photo storage.
            door_location: Dict with x, y coordinates of front door.
            drop_off_location: Dict with x, y coordinates of package drop-off.
        """
        self.brain = thinkneo_brain
        self.mqtt = mqtt_client
        self.minio = minio_client
        self.door_location = door_location or {"x": 0.5, "y": 5.0}
        self.drop_off_location = drop_off_location or {"x": 3.0, "y": 2.0}
        self.active_deliveries: list[DeliveryEvent] = []
        self.completed_deliveries: list[DeliveryEvent] = []
        self._delivery_counter = 0

        logger.info(
            "DeliveryIntake initialized — door=%s, drop_off=%s",
            self.door_location,
            self.drop_off_location,
        )

    # ------------------------------------------------------------------
    # Trigger detection
    # ------------------------------------------------------------------

    def on_audio_event(self, event: dict) -> Optional[DeliveryEvent]:
        """
        Process an audio event that might indicate a delivery.

        Args:
            event: Dict with type (doorbell, knock), confidence.

        Returns:
            DeliveryEvent if a delivery workflow should be started.
        """
        event_type = event.get("type", "")
        confidence = event.get("confidence", 0)

        if event_type in ("doorbell", "knock") and confidence > 0.7:
            logger.info(
                "Delivery trigger detected: %s (confidence: %.2f)",
                event_type, confidence,
            )
            trigger = (
                DeliveryTrigger.DOORBELL
                if event_type == "doorbell"
                else DeliveryTrigger.KNOCK
            )
            return self.start_delivery(trigger)

        return None

    def on_vision_event(self, detections: list[dict], room: str) -> Optional[DeliveryEvent]:
        """
        Process vision detections near the front door.

        Args:
            detections: List of YOLOv8 detections.
            room: Room where detection occurred.

        Returns:
            DeliveryEvent if a person or package is detected at the door.
        """
        if room != "entrance":
            return None

        person_at_door = any(
            d.get("class") == "person" and d.get("confidence", 0) > 0.6
            for d in detections
        )
        package_on_ground = any(
            d.get("class") in ("suitcase", "backpack", "handbag")
            and d.get("confidence", 0) > 0.5
            for d in detections
        )

        if person_at_door:
            return self.start_delivery(DeliveryTrigger.PERSON_AT_DOOR)
        elif package_on_ground:
            return self.start_delivery(DeliveryTrigger.PACKAGE_ON_GROUND)

        return None

    # ------------------------------------------------------------------
    # Delivery workflow
    # ------------------------------------------------------------------

    def start_delivery(self, trigger: DeliveryTrigger) -> DeliveryEvent:
        """Start a new delivery reception workflow."""
        self._delivery_counter += 1
        delivery_id = f"DEL-{self._delivery_counter:04d}"

        event = DeliveryEvent(
            delivery_id=delivery_id,
            trigger=trigger,
        )
        self.active_deliveries.append(event)

        logger.info(
            "Delivery workflow started: %s (trigger: %s)",
            delivery_id, trigger.value,
        )

        # Execute workflow steps
        self._navigate_to_door(event)
        self._identify_person(event)
        self._assess_package(event)
        self._capture_evidence(event)
        self._receive_package(event)
        self._transport_to_dropoff(event)
        self._notify_owner(event)
        self._complete_delivery(event)

        return event

    # ------------------------------------------------------------------
    # Workflow steps (skeleton implementations)
    # ------------------------------------------------------------------

    def _navigate_to_door(self, event: DeliveryEvent):
        """Navigate robot to the front door."""
        event.status = DeliveryStatus.NAVIGATING_TO_DOOR
        event.notes.append("Navigating to front door")

        logger.info(
            "[%s] Navigating to door at %s",
            event.delivery_id, self.door_location,
        )

        if self.mqtt:
            self.mqtt.publish(
                "fofoca/command/navigate",
                json.dumps(self.door_location),
            )

        # Skeleton: wait for navigation to complete
        # In production: subscribe to /fofoca/nav/status and wait for "arrived"
        event.status = DeliveryStatus.AT_DOOR
        event.notes.append("Arrived at front door")

    def _identify_person(self, event: DeliveryEvent):
        """Identify the person at the door using face recognition."""
        event.status = DeliveryStatus.IDENTIFYING

        logger.info("[%s] Identifying person at door", event.delivery_id)

        # Skeleton: In production, capture frame and run InsightFace
        # face_embedding = insightface.get_embedding(frame)
        # match = face_db.search(face_embedding, threshold=0.6)

        # Simulated result
        event.person_identified = False
        event.person_name = None
        event.person_confidence = 0.0
        event.notes.append("Person identification attempted")

    def _assess_package(self, event: DeliveryEvent):
        """Assess the package size to determine if gripper can handle it."""
        logger.info("[%s] Assessing package", event.delivery_id)

        # Skeleton: In production, use YOLOv8 bbox dimensions
        # to estimate package size relative to robot gripper
        event.package_detected = True
        event.package_size = "small"  # small = gripper can handle
        event.notes.append(f"Package assessed: size={event.package_size}")

    def _capture_evidence(self, event: DeliveryEvent):
        """Capture a photo of the delivery as evidence."""
        logger.info("[%s] Capturing evidence photo", event.delivery_id)

        # Skeleton: In production, capture 360 frame from Insta360
        # save to MinIO, store path in event
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        photo_filename = f"delivery_{event.delivery_id}_{timestamp}.jpg"
        event.photo_path = f"deliveries/{photo_filename}"
        event.notes.append(f"Evidence captured: {event.photo_path}")

        if self.minio:
            # self.minio.put_object("fofoca", event.photo_path, frame_bytes)
            pass

    def _receive_package(self, event: DeliveryEvent):
        """Receive the package using the robotic arm gripper."""
        event.status = DeliveryStatus.RECEIVING

        if event.package_size == "small":
            logger.info(
                "[%s] Receiving small package with gripper", event.delivery_id
            )
            if self.mqtt:
                # Open gripper
                self.mqtt.publish(
                    "fofoca/command/arm",
                    json.dumps({"action": "gripper_open"}),
                )
                # Position arm for pickup
                self.mqtt.publish(
                    "fofoca/command/arm",
                    json.dumps({
                        "action": "move_to",
                        "position": "pickup_low",
                    }),
                )
                # Close gripper
                self.mqtt.publish(
                    "fofoca/command/arm",
                    json.dumps({"action": "gripper_close"}),
                )
                # Lift
                self.mqtt.publish(
                    "fofoca/command/arm",
                    json.dumps({
                        "action": "move_to",
                        "position": "carry",
                    }),
                )
            event.notes.append("Package received with gripper")
        else:
            logger.info(
                "[%s] Package too large for gripper — will guide placement",
                event.delivery_id,
            )
            event.notes.append("Package too large — guided placement only")

    def _transport_to_dropoff(self, event: DeliveryEvent):
        """Transport the package to the designated drop-off location."""
        event.status = DeliveryStatus.TRANSPORTING

        logger.info(
            "[%s] Transporting to drop-off at %s",
            event.delivery_id, self.drop_off_location,
        )

        if self.mqtt:
            self.mqtt.publish(
                "fofoca/command/navigate",
                json.dumps(self.drop_off_location),
            )

        # Skeleton: wait for navigation, then release gripper
        if event.package_size == "small" and self.mqtt:
            self.mqtt.publish(
                "fofoca/command/arm",
                json.dumps({"action": "gripper_open"}),
            )

        event.status = DeliveryStatus.STORED
        event.notes.append(
            f"Package stored at {event.drop_off_location}"
        )

    def _notify_owner(self, event: DeliveryEvent):
        """Notify the homeowner about the delivery."""
        logger.info("[%s] Notifying owner", event.delivery_id)

        notification = {
            "type": "delivery_received",
            "delivery_id": event.delivery_id,
            "person_identified": event.person_identified,
            "person_name": event.person_name,
            "package_size": event.package_size,
            "stored_at": event.drop_off_location,
            "photo": event.photo_path,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        if self.mqtt:
            self.mqtt.publish(
                "fofoca/notification/delivery",
                json.dumps(notification),
            )

        event.notes.append("Owner notified")

    def _complete_delivery(self, event: DeliveryEvent):
        """Mark the delivery as complete and archive it."""
        event.status = DeliveryStatus.COMPLETED
        event.timestamp_end = datetime.now(timezone.utc).isoformat()

        self.active_deliveries.remove(event)
        self.completed_deliveries.append(event)

        logger.info(
            "[%s] Delivery completed — duration: %s to %s",
            event.delivery_id,
            event.timestamp_start,
            event.timestamp_end,
        )

    # ------------------------------------------------------------------
    # Status and reporting
    # ------------------------------------------------------------------

    def get_status(self) -> dict:
        """Get current delivery intake status."""
        return {
            "active_deliveries": [asdict(d) for d in self.active_deliveries],
            "completed_today": len(self.completed_deliveries),
            "last_delivery": (
                asdict(self.completed_deliveries[-1])
                if self.completed_deliveries
                else None
            ),
        }

    def get_delivery_log(self) -> list[dict]:
        """Get full delivery log for audit purposes."""
        return [asdict(d) for d in self.completed_deliveries]


# ---------------------------------------------------------------------------
# Standalone test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    intake = DeliveryIntake()

    # Simulate doorbell detection
    event = intake.on_audio_event({
        "type": "doorbell",
        "confidence": 0.92,
        "duration_ms": 500,
    })

    if event:
        print(f"\nDelivery completed: {json.dumps(asdict(event), indent=2)}")

    # Print status
    print(f"\nStatus: {json.dumps(intake.get_status(), indent=2)}")
