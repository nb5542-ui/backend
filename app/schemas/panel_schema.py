from pydantic import BaseModel, Field
from typing import List

class Dialogue(BaseModel):
    speaker: str
    text: str

class Action(BaseModel):
    description: str

class Emotion(BaseModel):
    character: str
    emotion: str
    intensity: float = Field(ge=0, le=1)

class Visual(BaseModel):
    setting: str
    characters: List[str]
    details: str

class Camera(BaseModel):
    shot_type: str
    angle: str

class Panel(BaseModel):
    dialogue: List[Dialogue]
    action: List[Action]
    emotion: List[Emotion]
    visual: Visual
    camera: Camera