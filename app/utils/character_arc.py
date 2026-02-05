from typing import Dict, List
from statistics import pstdev
from pydantic import BaseModel


class CharacterArc(BaseModel):
    character_id: str

    emotional_trend: Dict[str, float]
    relationship_trend: Dict[str, float]

    arc_type: str  # growth | regression | static | volatile
    confidence: float

    explanation: List[str]


# -----------------------------
# Helpers
# -----------------------------

def emotion_magnitude(state: Dict[str, float]) -> float:
    return sum(abs(v) for v in state.values())


def compute_trend(series: List[float]) -> float:
    if len(series) < 2:
        return 0.0
    return series[-1] - series[0]


def classify_arc(emotion_delta: float, volatility: float) -> str:
    if abs(emotion_delta) < 0.1 and volatility < 0.2:
        return "static"

    if volatility > 0.6:
        return "volatile"

    if emotion_delta > 0.1:
        return "growth"

    if emotion_delta < -0.1:
        return "regression"

    return "static"


# -----------------------------
# Main Analyzer
# -----------------------------

def analyze_character_arc(story, character_id: str) -> CharacterArc:
    emotion_series: List[float] = []
    relationship_series: List[float] = []
    explanation: List[str] = []

    character = next(
        (c for c in story.characters if c.id == character_id),
        None
    )

    if not character:
        return CharacterArc(
            character_id=character_id,
            emotional_trend={},
            relationship_trend={},
            arc_type="static",
            confidence=0.0,
            explanation=["Character not found in story"]
        )

    for chapter in story.chapters:
        for page in chapter.pages:
            for panel in page.panels:
                if character_id not in panel.characters_present:
                    continue

                mag = emotion_magnitude(character.emotional_state)

                if panel.focus_character == character_id:
                    mag *= 1.3  # focus weighting

                emotion_series.append(mag)

                rel_score = 0.0
                for r in character.relationships:
                    rel_score += r.trust - r.hostility + r.familiarity

                relationship_series.append(rel_score)

    if not emotion_series:
        return CharacterArc(
            character_id=character_id,
            emotional_trend={},
            relationship_trend={},
            arc_type="static",
            confidence=0.0,
            explanation=["Insufficient panel data for arc analysis"]
        )

    emotion_delta = compute_trend(emotion_series)
    volatility = pstdev(emotion_series) if len(emotion_series) > 1 else 0.0
    relationship_delta = compute_trend(relationship_series)

    arc_type = classify_arc(emotion_delta, volatility)

    explanation.append(
        f"Emotional change across panels: {round(emotion_delta, 3)}"
    )
    explanation.append(
        f"Emotional volatility: {round(volatility, 3)}"
    )

    return CharacterArc(
        character_id=character_id,
        emotional_trend={
            "delta": round(emotion_delta, 3),
            "volatility": round(volatility, 3)
        },
        relationship_trend={
            "delta": round(relationship_delta, 3)
        },
        arc_type=arc_type,
        confidence=min(1.0, len(emotion_series) / 10),
        explanation=explanation
    )
