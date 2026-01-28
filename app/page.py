from pydantic import BaseModel, Field
from typing import List
from app.utils.ids import new_id
from app.panel import Panel


class Page(BaseModel):
    """
    Layout container.
    Holds panels, no story intelligence.
    """
    id: str = Field(default_factory=new_id)

    # Order inside chapter (1-based)
    order: int = 1

    # Panels on this page
    panels: List[Panel] = Field(default_factory=list)
