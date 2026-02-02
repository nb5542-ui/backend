from pydantic import BaseModel, Field
from typing import Dict
from app.utils.ids import new_id


class VisualIntent(BaseModel):
    description: str = ""
    camera: str = "medium"
    mood: str = "neutral"


class Panel(BaseModel):
    id: str = Field(default_factory=new_id)

    story_beat: str
    tension: int

    narration: str = ""
    dialogue: str = ""

    visual_intent: VisualIntent = VisualIntent()

    locked: bool = False
    metadata: Dict = {}
