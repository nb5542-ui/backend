from typing import List
from pydantic import BaseModel


class BeatExplanation(BaseModel):
    panel_id: str
    story_beat: str

    justification: List[str]
    cautions: List[str]

    confidence: float


def explain_beat(story, panel) -> BeatExplanation:
    justification: List[str] = []
    cautions: List[str] = []

    # ----------------------------------
    # Collect all panels in order
    # ----------------------------------
    all_panels = []
    for chapter in story.chapters:
        for page in chapter.pages:
            for p in page.panels:
                all_panels.append(p)

    if panel not in all_panels:
        return BeatExplanation(
            panel_id=panel.id,
            story_beat=panel.story_beat,
            justification=[],
            cautions=["Panel not found in story timeline"],
            confidence=0.0
        )

    index = all_panels.index(panel)
    previous_panels = all_panels[max(0, index - 3):index]

    # ----------------------------------
    # 1. Tension progression check
    # ----------------------------------
    if previous_panels:
        avg_tension = sum(p.tension for p in previous_panels) / len(previous_panels)
        if abs(panel.tension - avg_tension) <= 20:
            justification.append(
                "Tension progression is consistent with recent panels"
            )
        else:
            cautions.append(
                "Tension shift is abrupt compared to recent context"
            )

    # ----------------------------------
    # 2. Beat continuity
    # ----------------------------------
    if previous_panels:
        prev_beat = previous_panels[-1].story_beat
        if prev_beat == panel.story_beat:
            justification.append(
                "Beat continuation reinforces the current narrative moment"
            )

    # ----------------------------------
    # 3. Character focus & emotion
    # ----------------------------------
    focus_id = panel.focus_character
    character = next(
        (c for c in story.characters if c.id == focus_id),
        None
    )

    if character:
        emotion_intensity = sum(
            abs(v) for v in character.emotional_state.values()
        )

        if emotion_intensity > 0.5:
            justification.append(
                "Focused character's emotional intensity supports this beat"
            )
        else:
            cautions.append(
                "Focused character emotional intensity is relatively low for this beat"
            )

    # ----------------------------------
    # 4. Intent alignment (soft)
    # ----------------------------------
    if story.intent:
        if panel.story_beat in ["inciting_incident", "climax", "resolution"]:
            justification.append(
                "Beat aligns with the declared story intent trajectory"
            )

    # ----------------------------------
    # Confidence heuristic
    # ----------------------------------
    confidence = min(
        1.0,
        0.3 + (0.15 * len(justification)) - (0.1 * len(cautions))
    )

    return BeatExplanation(
        panel_id=panel.id,
        story_beat=panel.story_beat,
        justification=justification,
        cautions=cautions,
        confidence=round(max(confidence, 0.0), 2)
    )
