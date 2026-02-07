from typing import List, Dict
from pydantic import BaseModel

from app.utils.beats import STORY_BEATS


class IntentDriftSnapshot(BaseModel):
    panel_id: str
    index: int
    dominant_emotions: List[str]
    dominant_themes: List[str]
    intensity: str
    drift_flags: List[str]


class IntentTimeline(BaseModel):
    total_panels: int
    drifted_panels: int
    drift_ratio: float
    timeline: List[IntentDriftSnapshot]


def build_intent_timeline(story, window_size: int = 4) -> IntentTimeline:
    """
    Analyze intent drift across the story timeline.
    """

    if not story.intent:
        return IntentTimeline(
            total_panels=0,
            drifted_panels=0,
            drift_ratio=0.0,
            timeline=[]
        )

    panels = []
    for chapter in story.chapters:
        for page in chapter.pages:
            panels.extend(page.panels)

    timeline: List[IntentDriftSnapshot] = []
    drifted = 0

    for idx, panel in enumerate(panels):
        beat = STORY_BEATS.get(panel.story_beat)
        if not beat:
            continue

        drift_flags = []

        # ---- emotional drift
        dominant_emotions = beat.get("emotional_shift", [])
        target_emotions = set(story.intent.emotional_targets)

        if target_emotions and not target_emotions.intersection(dominant_emotions):
            drift_flags.append("emotional_drift")

        # ---- thematic drift
        dominant_themes = beat.get("theme_affinity", [])
        target_themes = set(story.intent.themes)

        if target_themes and not target_themes.intersection(dominant_themes):
            drift_flags.append("theme_drift")

        # ---- pacing drift
        intensity = beat.get("intensity")
        pacing = story.intent.pacing_profile.get("overall")

        if pacing == "slow-burn" and intensity == "high":
            drift_flags.append("pacing_drift")

        if pacing == "fast" and intensity == "low":
            drift_flags.append("pacing_drift")

        if drift_flags:
            drifted += 1

        timeline.append(
            IntentDriftSnapshot(
                panel_id=panel.id,
                index=idx,
                dominant_emotions=dominant_emotions,
                dominant_themes=dominant_themes,
                intensity=intensity,
                drift_flags=drift_flags
            )
        )

    total = len(timeline)
    ratio = drifted / total if total else 0.0

    return IntentTimeline(
        total_panels=total,
        drifted_panels=drifted,
        drift_ratio=round(ratio, 2),
        timeline=timeline
    )
