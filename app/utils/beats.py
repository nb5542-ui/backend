from typing import Dict, List, Set


Beat = Dict[str, object]


STORY_BEATS: Dict[str, Beat] = {
    "introduction": {
        "emotional_shift": ["curiosity"],
        "preferred_position": (0.0, 0.15),
        "intensity": "low",
        "theme_affinity": []
    },
    "inciting_incident": {
        "emotional_shift": ["shock", "tension"],
        "preferred_position": (0.1, 0.25),
        "intensity": "medium",
        "theme_affinity": ["power", "loss"]
    },
    "rising_tension": {
        "emotional_shift": ["tension"],
        "preferred_position": (0.2, 0.45),
        "intensity": "medium",
        "theme_affinity": []
    },
    "conflict": {
        "emotional_shift": ["anger", "fear"],
        "preferred_position": (0.3, 0.6),
        "intensity": "high",
        "theme_affinity": ["identity"]
    },
    "revelation": {
        "emotional_shift": ["shock", "unease"],
        "preferred_position": (0.4, 0.7),
        "intensity": "high",
        "theme_affinity": ["truth", "identity"]
    },
    "climax": {
        "emotional_shift": ["overwhelm"],
        "preferred_position": (0.6, 0.85),
        "intensity": "very_high",
        "theme_affinity": []
    },
    "fallout": {
        "emotional_shift": ["exhaustion", "sadness"],
        "preferred_position": (0.75, 0.95),
        "intensity": "low",
        "theme_affinity": []
    },
    "resolution": {
        "emotional_shift": ["closure"],
        "preferred_position": (0.85, 1.0),
        "intensity": "low",
        "theme_affinity": []
    },
    "cliffhanger": {
        "emotional_shift": ["anticipation"],
        "preferred_position": (0.3, 0.95),
        "intensity": "medium",
        "theme_affinity": []
    },
    "quiet_moment": {
        "emotional_shift": ["reflection"],
        "preferred_position": (0.0, 1.0),
        "intensity": "low",
        "theme_affinity": []
    }
}


def is_valid_beat(beat: str) -> bool:
    return bool(beat) and beat in STORY_BEATS


def filter_valid_beats(
    story_progress: float,
    beats_used: Set[str]
) -> List[str]:
    valid = []
    for beat_id, beat in STORY_BEATS.items():
        if beat_id in beats_used:
            continue
        min_p, max_p = beat["preferred_position"]
        if min_p <= story_progress <= max_p:
            valid.append(beat_id)
    return valid


def score_beat(
    beat_id: str,
    beat_data: dict,
    intent: dict
) -> int:
    score = 0

    # Narrative goal bias
    goal_map = {
        "psychological_descent": {
            "conflict": 2,
            "revelation": 3,
            "quiet_moment": 2
        },
        "hero_journey": {
            "rising_tension": 2,
            "climax": 3,
            "resolution": 2
        }
    }

    goal = intent.get("narrative_goal")
    if goal in goal_map:
        score += goal_map[goal].get(beat_id, 0)

    # Emotional targets
    for emotion in intent.get("emotional_targets", []):
        if emotion in beat_data["emotional_shift"]:
            score += 1

    # Theme affinity
    for theme in intent.get("themes", []):
        if theme in beat_data["theme_affinity"]:
            score += 1

    # Pacing bias
    pacing = intent.get("pacing_profile", {}).get("overall", "balanced")
    if pacing == "slow-burn" and beat_data["intensity"] == "low":
        score += 1
    if pacing == "fast" and beat_data["intensity"] in {"high", "very_high"}:
        score += 1

    return score


def recommend_beats(
    story_progress: float,
    beats_used: Set[str],
    intent: dict
) -> List[dict]:
    candidates = filter_valid_beats(story_progress, beats_used)

    ranked = []
    for beat_id in candidates:
        ranked.append({
            "beat": beat_id,
            "score": score_beat(
                beat_id,
                STORY_BEATS[beat_id],
                intent
            )
        })

    ranked.sort(key=lambda x: x["score"], reverse=True)
    return ranked
