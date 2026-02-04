from pydantic import BaseModel, Field
from typing import List, Dict
from app.utils.ids import new_id


class Character(BaseModel):
    """
    Persistent narrative actor.
    """

    id: str = Field(default_factory=new_id)

    name: str
    role: str = "support"  # protagonist, antagonist, support

    traits: List[str] = Field(
        default_factory=list,
        description="Stable personality traits"
    )

    emotional_state: Dict[str, float] = Field(
        default_factory=lambda: {
            "fear": 0.0,
            "confidence": 0.0,
            "anger": 0.0
        },
        description="Lightweight emotional signals (0–1)"
    )

    metadata: Dict = Field(
        default_factory=dict,
        description="Free-form extension space"
    )
