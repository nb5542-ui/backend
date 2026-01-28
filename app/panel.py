from pydantic import BaseModel, Field
from typing import Dict
from app.utils.ids import new_id


class VisualIntent(BaseModel):
    """
    Describes what should be drawn.
    NOT narration. NOT dialogue.
    """
    description: str
    camera: str = "medium"
    mood: str = "neutral"


class Panel(BaseModel):
    """
    Atomic visual unit.
    Panels are NEVER reused.
    """
    id: str = Field(default_factory=new_id)

    # Core story meaning
    story_beat: str = ""

    # User-visible text
    narration: str = ""
    dialogue: str = ""

    # Visual direction
    visual_intent: VisualIntent = Field(
        default_factory=lambda: VisualIntent(description="")
    )

    # Editing / future use
    locked: bool = False
    metadata: Dict = Field(default_factory=dict)
