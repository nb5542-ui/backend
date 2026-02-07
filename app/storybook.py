from typing import List, Optional
from pydantic import BaseModel, Field
from uuid import uuid4

from app.character import Character
from app.chapter import Chapter
from app.panel import Panel


class Storybook(BaseModel):
    """
    Root aggregate for a story.
    Owns characters, chapters, and all traversal logic.
    """

    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str

    characters: List[Character] = Field(default_factory=list)
    chapters: List[Chapter] = Field(default_factory=list)

    # Story intent is OPTIONAL and added later
    intent: Optional[object] = None

    # ---------------------------
    # Character helpers
    # ---------------------------

    def add_character(self, character: Character):
        self.characters.append(character)

    def get_character(self, character_id: str) -> Optional[Character]:
        for c in self.characters:
            if c.id == character_id:
                return c
        return None

    # ---------------------------
    # Chapter helpers
    # ---------------------------

    def add_chapter(self, chapter: Chapter):
        self.chapters.append(chapter)

    def get_chapter(self, chapter_id: str) -> Optional[Chapter]:
        for ch in self.chapters:
            if ch.id == chapter_id:
                return ch
        return None

    # ---------------------------
    # Page helpers
    # ---------------------------

    def get_page(self, chapter_id: str, page_id: str):
        chapter = self.get_chapter(chapter_id)
        if not chapter:
            return None

        for page in chapter.pages:
            if page.id == page_id:
                return page
        return None

    # ---------------------------
    # Panel helpers (CRITICAL)
    # ---------------------------

    def find_panel(self, panel_id: str) -> Optional[Panel]:
        """
        Canonical way to locate a panel anywhere in the story.
        """
        for chapter in self.chapters:
            for page in chapter.pages:
                for panel in page.panels:
                    if panel.id == panel_id:
                        return panel
        return None

    def all_panels_in_order(self) -> List[Panel]:
        """
        Returns all panels in strict narrative order.
        """
        panels: List[Panel] = []
        for chapter in self.chapters:
            for page in chapter.pages:
                panels.extend(page.panels)
        return panels
