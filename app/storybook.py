from pydantic import BaseModel, Field
from typing import List, Dict
from app.utils.ids import new_id
from app.chapter import Chapter
from app.story_intent import StoryIntent


class Storybook(BaseModel):
    """
    Root aggregate of the entire story.
    """

    id: str = Field(default_factory=new_id)

    meta: Dict = Field(
        default_factory=lambda: {
            "title": "Untitled Story",
            "author": "Anonymous",
        }
    )

    intent: StoryIntent = Field(default_factory=StoryIntent)

    chapters: List[Chapter] = Field(default_factory=list)
