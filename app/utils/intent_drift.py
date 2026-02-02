from typing import List, Dict
from app.utils.beats import STORY_BEATS


def detect_intent_drift(
    recent_beats: List[str],
    intent: Dict,
    window_size: int = 5
) -> Dict:
    """
    Analyze recent beats and detect drift from story intent.
    Returns warnings, not errors.
    """

    recent_beats = recent_beats[-window_size:]

    emotional_hits = {}
    theme_hits = {}
    intensity_levels = []

    # -----------------------------
    # Aggregate signals
    # -----------------------------
    for beat_id in recent_beats:
        beat = STORY_BEATS.get(beat_id)
        if not beat:
            continue

        for emotion in beat["emotional_shift"]:
            emotional_hits[emotion] = emotional_hits.get(emotion, 0) + 1

        for theme in beat["theme_affinity"]:
            theme_hits[theme] = theme_hits.get(theme, 0) + 1

        intensity_levels.append(beat["intensity"])

    warnings = []

    # -----------------------------
    # Emotional Drift
    # -----------------------------
    target_emotions = set(intent.get("emotional_targets", []))
    if target_emotions:
        dominant_emotions = {
            e for e, count in emotional_hits.items() if count >= 2
        }

        if dominant_emotions and not dominant_emotions & target_emotions:
            warnings.append({
                "type": "emotional_drift",
                "message": (
                    f"Recent emotions {list(dominant_emotions)} "
                    f"do not align with intent {list(target_emotions)}"
                )
            })

    # -----------------------------
    # Thematic Drift
    # -----------------------------
    target_themes = set(intent.get("themes", []))
    if target_themes:
        dominant_themes = {
            t for t, count in theme_hits.items() if count >= 2
        }

        if dominant_themes and not dominant_themes & target_themes:
            warnings.append({
                "type": "theme_drift",
                "message": (
                    f"Recent themes {list(dominant_themes)} "
                    f"do not align with intent {list(target_themes)}"
                )
            })

    # -----------------------------
    # Pacing Drift
    # -----------------------------
    pacing = intent.get("pacing_profile", {}).get("overall")

    if pacing == "slow-burn" and intensity_levels.count("high") >= 3:
        warnings.append({
            "type": "pacing_drift",
            "message": "Too many high-intensity beats for slow-burn pacing"
        })

    if pacing == "fast" and intensity_levels.count("low") >= 3:
        warnings.append({
            "type": "pacing_drift",
            "message": "Too many low-intensity beats for fast pacing"
        })

    return {
        "drift_detected": bool(warnings),
        "warnings": warnings
    }
