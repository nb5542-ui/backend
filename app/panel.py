from pydantic import BaseModel, Field, validator
from typing import Dict
from app.utils.ids import new_id
from app.utils.beats import is_valid_beat
from app.utils.pacing import is_valid_tension


class VisualIntent(BaseModel):
    description: str = ""
    camera: str = "medium"
    mood: str = "neutral"


class Panel(BaseModel):
    id: str = Field(default_factory=new_id)

    story_beat: str
    tension: int = 30  # default calm-forward motion

    narration: str = ""
    dialogue: str = ""

    visual_intent: VisualIntent = VisualIntent()

    locked: bool = False
    metadata: Dict = {}

    @validator("story_beat")
    def validate_story_beat(cls, v):
        if not is_valid_beat(v):
            raise ValueError(f"Invalid story beat: '{v}'")
        return v

    @validator("tension")
    def validate_tension(cls, v):
        if not is_valid_tension(v):
            raise ValueError("Tension must be between 0 and 100")
        return v
