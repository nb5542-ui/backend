from pydantic import BaseModel, Field
from typing import List, Dict, Tuple, Optional


class StoryIntent(BaseModel):
    """
    High-level creative intent for a story.
    Observed, never enforced.
    """

    narrative_goal: str = Field(
        default="open_ended",
        description="Overall narrative direction"
    )

    # Target reader-facing emotions
    emotional_targets: List[str] = Field(
        default_factory=list
    )

    # Narrative themes to emphasize
    themes: List[str] = Field(
        default_factory=list
    )

    # Expected pacing behavior
    pacing_profile: Dict[str, str] = Field(
        default_factory=lambda: {
            "overall": "balanced"  # slow-burn | balanced | fast
        }
    )

    # --- NEW (crucial for drift scoring) ---

    target_tension_range: Tuple[int, int] = (
        30, 70
    )

    emotional_volatility: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="0 = very stable, 1 = very volatile"
    )

    relationship_focus: Optional[List[str]] = Field(
        default=None,
        description="Character IDs whose relationships should matter"
    )
