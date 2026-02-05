from pydantic import BaseModel, Field
from typing import List, Dict
from app.utils.ids import new_id


# --------------------------------------------------
# Relationship Model (Directed)
# --------------------------------------------------

class Relationship(BaseModel):
    target_character_id: str

    trust: float = 0.0        # -1.0 → 1.0
    hostility: float = 0.0    # 0.0 → 1.0
    familiarity: float = 0.0 # 0.0 → 1.0


# --------------------------------------------------
# Character Model
# --------------------------------------------------

class Character(BaseModel):
    """
    Persistent narrative actor.
    """

    id: str = Field(default_factory=new_id)

    name: str
    role: str = "support"  # protagonist, antagonist, support

    traits: List[str] = Field(default_factory=list)

    emotional_state: Dict[str, float] = Field(
        default_factory=lambda: {
            "fear": 0.0,
            "confidence": 0.0,
            "anger": 0.0
        }
    )

    relationships: List[Relationship] = Field(
        default_factory=list,
        description="Directed relationships to other characters"
    )

    metadata: Dict = Field(default_factory=dict)
