from pydantic import BaseModel, Field
from typing import Optional, Dict
from app.utils.ids import new_id


class VisualIntent(BaseModel):
    description: str = ""
    camera: str = "medium"
    mood: str = "neutral"


class Panel(BaseModel):
    """
    Atomic unit of a manga page.
    This is where story, narration, and visuals converge.
    """
    id: str = Field(default_factory=new_id)

    story_beat: str = ""
    narration: str = ""
    dialogue: str = ""

    visual_intent: VisualIntent = Field(default_factory=VisualIntent)

    locked: bool = False
    metadata: Dict = Field(default_factory=dict)
