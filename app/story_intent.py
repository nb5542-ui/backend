from pydantic import BaseModel, Field
from typing import List, Dict


class StoryIntent(BaseModel):
    """
    High-level creative intent for a story.
    Biases narrative decisions but never enforces them.
    """

    narrative_goal: str = Field(
        default="open_ended",
        description="Overall narrative direction"
    )

    emotional_targets: List[str] = Field(
        default_factory=list,
        description="Target reader emotions"
    )

    themes: List[str] = Field(
        default_factory=list,
        description="Core narrative themes"
    )

    pacing_profile: Dict[str, str] = Field(
        default_factory=lambda: {
            "overall": "balanced"
        },
        description="Narrative pacing preferences"
    )
