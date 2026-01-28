from pydantic import BaseModel, Field
from typing import List
from app.utils.ids import new_id
from app.page import Page


class Chapter(BaseModel):
    """
    Ordered collection of pages.
    """
    id: str = Field(default_factory=new_id)

    # Order in storybook (1-based)
    order: int = 1

    title: str = "Untitled Chapter"

    pages: List[Page] = Field(default_factory=list)
