from pydantic import BaseModel, Field
from typing import Dict, Optional


class CharacterCanon(BaseModel):
    alive: Optional[bool] = True
    role: Optional[str] = None


class RelationshipCanon(BaseModel):
    status: Optional[str] = None  # ally | enemy | neutral
    locked: bool = False


class CanonRegistry(BaseModel):
    characters: Dict[str, CharacterCanon] = Field(default_factory=dict)
    relationships: Dict[str, RelationshipCanon] = Field(default_factory=dict)
