from typing import Dict


# Clamp values between 0 and 1
def clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def compute_emotional_drift(
    current_state: Dict[str, float],
    *,
    story_beat: str,
    tension: int,
    is_focus: bool
) -> Dict[str, float]:
    """
    Compute next emotional state for a character
    based on panel signals.
    """

    delta = {
        "fear": 0.0,
        "confidence": 0.0,
        "anger": 0.0
    }

    # -----------------------------
    # Beat-based influence
    # -----------------------------
    if story_beat in {"conflict", "climax"}:
        delta["anger"] += 0.05
        delta["fear"] += 0.05

    if story_beat in {"revelation"}:
        delta["fear"] += 0.1

    if story_beat in {"resolution", "quiet_moment"}:
        delta["confidence"] += 0.05
        delta["fear"] -= 0.05

    # -----------------------------
    # Tension scaling
    # -----------------------------
    tension_factor = tension / 100.0
    delta["fear"] += 0.1 * tension_factor

    # -----------------------------
    # Focus amplification
    # -----------------------------
    if is_focus:
        for k in delta:
            delta[k] *= 1.5

    # -----------------------------
    # Apply + clamp
    # -----------------------------
    new_state = {}
    for emotion, value in current_state.items():
        new_state[emotion] = clamp(value + delta.get(emotion, 0.0))

    return new_state
