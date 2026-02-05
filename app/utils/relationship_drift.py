from typing import Dict


def clamp(value: float, min_v: float, max_v: float) -> float:
    return max(min_v, min(max_v, value))


def compute_relationship_drift(
    *,
    current: Dict[str, float],
    story_beat: str,
    tension: int,
    is_focus: bool
) -> Dict[str, float]:
    """
    Compute how a relationship shifts after a panel.
    """

    delta = {
        "trust": 0.0,
        "hostility": 0.0,
        "familiarity": 0.02
    }

    # -----------------------------
    # Beat-based influence
    # -----------------------------
    if story_beat in {"conflict", "climax"}:
        delta["hostility"] += 0.05
        delta["trust"] -= 0.03

    if story_beat in {"quiet_moment", "resolution"}:
        delta["trust"] += 0.05
        delta["hostility"] -= 0.03

    # -----------------------------
    # Tension scaling
    # -----------------------------
    tension_factor = tension / 100.0
    delta["hostility"] += 0.05 * tension_factor

    # -----------------------------
    # Focus amplification
    # -----------------------------
    if is_focus:
        for k in delta:
            delta[k] *= 1.5

    # -----------------------------
    # Apply + clamp
    # -----------------------------
    return {
        "trust": clamp(current["trust"] + delta["trust"], -1.0, 1.0),
        "hostility": clamp(current["hostility"] + delta["hostility"], 0.0, 1.0),
        "familiarity": clamp(current["familiarity"] + delta["familiarity"], 0.0, 1.0),
    }
