from pydantic import BaseModel, Field
from typing import List
from app.utils.ids import new_id
from app.panel import Panel


class Page(BaseModel):
    """
    A page is a layout container for panels.
    It has NO story intelligence itself.
    """
    id: str = Field(default_factory=new_id)
    order: int
    panels: List[Panel] = Field(default_factory=list)
