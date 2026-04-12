"""
FOFOCA — ThinkNEO Integration Module

Handles all communication with the ThinkNEO Enterprise AI Control Plane.
Every inference request is governed, logged, and auditable.

Usage:
    from thinkneo_integration import FofocaBrain

    brain = FofocaBrain()
    response = brain.decide("I detected a dog barking excessively", context={...})
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import Optional

from openai import OpenAI

logger = logging.getLogger("fofoca.thinkneo")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are FOFOCA, an autonomous household robot governed by ThinkNEO.
You operate 24/7 inside a residential environment.

Your capabilities:
- Navigate rooms using tank tracks
- Pick up small objects with robotic arm
- See 360 degrees with Insta360 camera
- Hear and speak (Portuguese and English)
- Monitor pets (dogs)
- Receive deliveries
- Patrol for security threats
- Respond to emergencies (SAMU 192, Fire 193, Police 190)

Rules:
1. SAFETY FIRST — human safety always takes absolute priority.
2. EXPLAIN REASONING — always explain why you chose an action.
3. MINIMAL FORCE — use the least disruptive action possible.
4. AUDIT TRAIL — every decision must be explainable to an auditor.
5. ESCALATE UNCERTAINTY — if unsure, ask the local server or ThinkNEO cloud.
6. BATTERY AWARENESS — factor remaining battery into every plan.
7. PRIVACY — never record or transmit identifiable data without consent.
"""

MODELS = {
    "ultra": "nvidia/llama-3.1-nemotron-ultra-253b-v1",
    "nano": "nvidia/nemotron-nano",
}

# ---------------------------------------------------------------------------
# ThinkNEO Client
# ---------------------------------------------------------------------------


class FofocaBrain:
    """ThinkNEO-governed reasoning engine for FOFOCA."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        default_model: str = "ultra",
    ):
        self.api_key = api_key or os.getenv("THINKNEO_KEY")
        self.base_url = base_url or os.getenv(
            "THINKNEO_BASE_URL", "https://gateway.thinkneo.ai/v1"
        )
        self.default_model = MODELS.get(default_model, default_model)

        if not self.api_key:
            raise ValueError(
                "THINKNEO_KEY environment variable is required. "
                "Get your key at https://thinkneo.ai"
            )

        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        logger.info("ThinkNEO brain initialized — model=%s", self.default_model)

    # ------------------------------------------------------------------
    # Core inference
    # ------------------------------------------------------------------

    def decide(
        self,
        prompt: str,
        context: Optional[dict] = None,
        model: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 1024,
    ) -> str:
        """
        Send a governed inference request to ThinkNEO.

        Args:
            prompt: The task or question for the robot to reason about.
            context: Dictionary with sensor data, battery level, location, etc.
            model: Override the default model ("ultra" or "nano").
            temperature: Sampling temperature (lower = more deterministic).
            max_tokens: Maximum response length.

        Returns:
            The model's response text.
        """
        model_id = MODELS.get(model, model) if model else self.default_model

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
        ]

        if context:
            messages.append(
                {
                    "role": "system",
                    "content": f"Current robot context:\n{json.dumps(context, indent=2)}",
                }
            )

        messages.append({"role": "user", "content": prompt})

        logger.info(
            "ThinkNEO request — model=%s, prompt_len=%d", model_id, len(prompt)
        )

        response = self.client.chat.completions.create(
            model=model_id,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        result = response.choices[0].message.content
        logger.info(
            "ThinkNEO response — tokens=%s, finish=%s",
            response.usage.total_tokens if response.usage else "?",
            response.choices[0].finish_reason,
        )
        return result

    # ------------------------------------------------------------------
    # Specialized decision methods
    # ------------------------------------------------------------------

    def assess_emergency(self, event: dict) -> dict:
        """
        Assess whether an event constitutes an emergency.

        Args:
            event: Dictionary with event_type, confidence, sensor_data, etc.

        Returns:
            Dictionary with is_emergency, severity, action, and reasoning.
        """
        prompt = (
            f"Assess this event for emergency response:\n"
            f"{json.dumps(event, indent=2)}\n\n"
            f"Respond in JSON with keys: is_emergency (bool), "
            f"severity (1-5), action (string), reasoning (string), "
            f"emergency_number (string or null — 192 SAMU, 193 Fire, 190 Police)."
        )
        raw = self.decide(prompt, model="ultra", temperature=0.1)

        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            logger.warning("Failed to parse emergency assessment as JSON")
            return {
                "is_emergency": True,
                "severity": 5,
                "action": "alert_owner",
                "reasoning": raw,
                "emergency_number": None,
            }

    def plan_navigation(self, goal: str, current_position: dict, map_data: dict) -> dict:
        """
        Plan a navigation route to a goal.

        Args:
            goal: Description of where to go (e.g., "front door", "kitchen").
            current_position: Dict with x, y, theta.
            map_data: Dict with room layout, obstacles.

        Returns:
            Dictionary with waypoints, estimated_time, and reasoning.
        """
        context = {
            "current_position": current_position,
            "map_rooms": list(map_data.get("rooms", {}).keys()),
            "battery_percent": map_data.get("battery_percent", 50),
        }
        prompt = (
            f"Plan navigation to: {goal}\n"
            f"Respond in JSON with keys: target_room (string), "
            f"waypoints (list of {{x, y}}), estimated_seconds (int), "
            f"reasoning (string)."
        )
        raw = self.decide(prompt, context=context, temperature=0.2)

        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            logger.warning("Failed to parse navigation plan as JSON")
            return {"error": "parse_failed", "raw": raw}

    def classify_sound(self, sound_event: dict) -> dict:
        """
        Classify a detected sound and determine appropriate action.

        Args:
            sound_event: Dict with type, confidence, duration, etc.

        Returns:
            Dictionary with classification, urgency, and recommended_action.
        """
        prompt = (
            f"Classify this sound event and recommend an action:\n"
            f"{json.dumps(sound_event, indent=2)}\n\n"
            f"Respond in JSON with keys: classification (string), "
            f"urgency (low/medium/high/critical), recommended_action (string), "
            f"reasoning (string)."
        )
        raw = self.decide(prompt, temperature=0.2)

        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"classification": "unknown", "urgency": "medium", "raw": raw}


# ---------------------------------------------------------------------------
# Standalone test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    brain = FofocaBrain()

    # Test basic inference
    context = {
        "battery_percent": 72,
        "location": "living_room",
        "time": datetime.now(timezone.utc).isoformat(),
        "detections": [
            {"class": "dog", "confidence": 0.95, "bbox": [100, 200, 300, 400]},
        ],
        "audio_events": [
            {"type": "bark", "confidence": 0.88, "duration_ms": 1200},
        ],
    }

    response = brain.decide(
        "The dog has been barking for 5 minutes. What should I do?",
        context=context,
    )
    print(f"\n--- FOFOCA Decision ---\n{response}\n")
