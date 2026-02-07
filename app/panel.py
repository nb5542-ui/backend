from pydantic import BaseModel, Field, model_validator
from typing import List, Optional

from app.utils.ids import new_id
from app.utils.beats import STORY_BEATS


class PanelCreate(BaseModel):
    story_beat: str
    tension: int
    characters_present: List[str]
    focus_character: str

    # STEP 8 — Scene / Location Awareness
    location: Optional[str] = None

    @model_validator(mode="after")
    def validate_panel(self):
        if self.story_beat not in STORY_BEATS:
            raise ValueError(f"Invalid story beat: {self.story_beat}")

        if self.focus_character not in self.characters_present:
            raise ValueError(
                "focus_character must be included in characters_present"
            )

        return self


class Panel(BaseModel):
    id: str = Field(default_factory=new_id)

    story_beat: str
    tension: int
    characters_present: List[str]
    focus_character: str

    # Scene metadata
    location: Optional[str] = None
    scene_id: Optional[str] = None
