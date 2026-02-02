from typing import Dict


# Positive weights encourage transitions
# Negative weights discourage them
BEAT_COUPLING: Dict[str, Dict[str, int]] = {
    "introduction": {
        "inciting_incident": 3,
        "quiet_moment": 1
    },
    "inciting_incident": {
        "rising_tension": 3,
        "conflict": 2
    },
    "rising_tension": {
        "conflict": 3,
        "revelation": 2,
        "quiet_moment": -1
    },
    "conflict": {
        "revelation": 3,
        "climax": 2
    },
    "revelation": {
        "fallout": 3,
        "quiet_moment": 2
    },
    "climax": {
        "fallout": 3,
        "resolution": 2
    },
    "fallout": {
        "resolution": 3,
        "quiet_moment": 1
    },
    "resolution": {},
    "cliffhanger": {
        "conflict": 2,
        "rising_tension": 2
    },
    "quiet_moment": {
        "rising_tension": 1,
        "revelation": 1
    }
}
def coupling_score(
    previous_beats: list[str],
    candidate_beat: str,
    window_size: int = 3
) -> int:
    """
    Scores how well a candidate beat follows recent beats.
    """
    score = 0
    recent = previous_beats[-window_size:]

    for prev in recent:
        transitions = BEAT_COUPLING.get(prev, {})
        score += transitions.get(candidate_beat, 0)

    return score
