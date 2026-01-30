# app/utils/beats.py

STORY_BEATS = {
    "setup",
    "introduction",
    "inciting_incident",
    "rising_tension",
    "conflict",
    "revelation",
    "climax",
    "fallout",
    "resolution",
    "cliffhanger",
    "quiet_moment"
}


def is_valid_beat(beat: str) -> bool:
    if not beat:
        return False
    return beat in STORY_BEATS
