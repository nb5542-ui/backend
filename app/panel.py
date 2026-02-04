from pydantic import BaseModel, Field, model_validator
from typing import Dict, List, Optional

from app.utils.ids import new_id
from app.utils.beats import is_valid_beat


# -----------------------------
# Visual Intent
# -----------------------------
class VisualIntent(BaseModel):
    description: str = ""
    camera: str = "medium"
    mood: str = "neutral"


# -----------------------------
# Panel Create DTO (REQUEST BODY)
# -----------------------------
class PanelCreate(BaseModel):
    story_beat: str
    tension: int = 30

    narration: str = ""
    dialogue: str = ""

    visual_intent: VisualIntent = VisualIntent()

    characters_present: List[str] = Field(default_factory=list)
    focus_character: Optional[str] = None

    @model_validator(mode="after")
    def validate_panel(self):
        # Validate beat
        if not is_valid_beat(self.story_beat):
            raise ValueError(f"Invalid story beat: {self.story_beat}")

        # Validate focus character
        if self.focus_character and self.focus_character not in self.characters_present:
            raise ValueError(
                "focus_character must be included in characters_present"
            )

        return self


# -----------------------------
# Panel Model (STORED OBJECT)
# -----------------------------
class Panel(BaseModel):
    id: str = Field(default_factory=new_id)

    story_beat: str
    tension: int

    narration: str = ""
    dialogue: str = ""

    visual_intent: VisualIntent = VisualIntent()

    characters_present: List[str] = Field(default_factory=list)
    focus_character: Optional[str] = None

    locked: bool = False
    metadata: Dict = {}
