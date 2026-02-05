from typing import Dict, List
from statistics import mean

from app.storybook import Storybook
from app.utils.story_intent import StoryIntent


def clamp(v: float, lo=0.0, hi=1.0):
    return max(lo, min(hi, v))


def analyze_intent_drift(story: Storybook) -> Dict:
    """
    Detects divergence between declared story intent
    and actual narrative execution.
    Read-only diagnostics.
    """

    if not story.intent:
        return {
            "drift_detected": False,
            "severity": "none",
            "score": 0.0,
            "warnings": ["No story intent declared"]
        }

    intent: StoryIntent = story.intent

    # -----------------------------
    # Collect execution signals
    # -----------------------------
    tensions = []
    emotion_magnitudes = []
    relationship_deltas = []

    recent_beats = []

    for chapter in story.chapters:
        for page in chapter.pages:
            for panel in page.panels:
                tensions.append(panel.tension)
                recent_beats.append(panel.story_beat)

                # Emotion drift magnitude
                if hasattr(panel, "emotion_drift"):
                    emotion_magnitudes.append(
                        sum(abs(v) for v in panel.emotion_drift.values())
                    )

                # Relationship drift magnitude
                if hasattr(panel, "relationship_drift"):
                    relationship_deltas.extend(
                        abs(v) for v in panel.relationship_drift.values()
                    )

    warnings = []

    # -----------------------------
    # TENSION DRIFT
    # -----------------------------
    tension_drift = 0.0
    if tensions:
        avg_tension = mean(tensions)
        low, high = intent.target_tension_range

        if not (low <= avg_tension <= high):
            tension_drift = clamp(
                min(abs(avg_tension - low), abs(avg_tension - high)) / 100
            )
            warnings.append(
                f"Average tension ({avg_tension:.1f}) outside intent range {low}-{high}"
            )

    # -----------------------------
    # EMOTIONAL DRIFT
    # -----------------------------
    emotion_drift = 0.0
    if emotion_magnitudes:
        avg_emotion = mean(emotion_magnitudes)
        expected = intent.emotional_volatility
        emotion_drift = clamp(abs(avg_emotion - expected))

        if emotion_drift > 0.4:
            warnings.append(
                "Emotional volatility diverges from declared intent"
            )

    # -----------------------------
    # RELATIONSHIP DRIFT
    # -----------------------------
    relationship_drift = 0.0
    if intent.relationship_focus and relationship_deltas:
        total = sum(relationship_deltas)
        if total == 0:
            relationship_drift = 1.0
            warnings.append("Declared relationship focus not reflected in panels")

    # -----------------------------
    # FINAL SCORE
    # -----------------------------
    score = clamp(
        (tension_drift + emotion_drift + relationship_drift) / 3
    )

    severity = (
        "none" if score < 0.15 else
        "mild" if score < 0.35 else
        "moderate" if score < 0.6 else
        "severe"
    )

    return {
        "drift_detected": score > 0.15,
        "severity": severity,
        "score": round(score, 3),
        "components": {
            "tension": round(tension_drift, 3),
            "emotion": round(emotion_drift, 3),
            "relationship": round(relationship_drift, 3),
        },
        "warnings": warnings
    }
