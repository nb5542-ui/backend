from fastapi import FastAPI, HTTPException

from app.storybook import Storybook
from app.chapter import Chapter
from app.page import Page
from app.panel import Panel

from app.store import STORIES
from app.utils.beats import STORY_BEATS
from app.utils.pacing import is_valid_progression


app = FastAPI(
    title="AI Manga Story Engine",
    version="0.2.0"
)

# --------------------------------------------------
# HEALTH
# --------------------------------------------------

@app.get("/health")
def health_check():
    return {"status": "ok"}


# --------------------------------------------------
# DISCOVERY / INTELLIGENCE
# --------------------------------------------------

@app.get("/beats")
def list_story_beats():
    """
    List all supported story beats.
    Used by frontend / AI planners later.
    """
    return sorted(STORY_BEATS)


# --------------------------------------------------
# STORY ENDPOINTS
# --------------------------------------------------

@app.post("/stories", response_model=Storybook)
def create_story():
    """
    Create a new empty story.
    """
    story = Storybook()
    STORIES[story.id] = story
    return story


@app.get("/stories", response_model=list[Storybook])
def list_stories():
    """
    List all stories.
    """
    return list(STORIES.values())


@app.get("/stories/{story_id}", response_model=Storybook)
def get_story(story_id: str):
    """
    Get a single story by ID.
    """
    story = STORIES.get(story_id)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    return story


# --------------------------------------------------
# CHAPTER ENDPOINTS
# --------------------------------------------------

@app.post("/stories/{story_id}/chapters", response_model=Chapter)
def add_chapter(story_id: str):
    """
    Add a chapter to a story.
    """
    story = STORIES.get(story_id)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")

    chapter = Chapter(
        order=len(story.chapters) + 1
    )

    story.chapters.append(chapter)
    return chapter


# --------------------------------------------------
# PAGE ENDPOINTS
# --------------------------------------------------

@app.post(
    "/stories/{story_id}/chapters/{chapter_id}/pages",
    response_model=Page
)
def add_page(story_id: str, chapter_id: str):
    """
    Add a page to a chapter.
    """
    story = STORIES.get(story_id)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")

    for chapter in story.chapters:
        if chapter.id == chapter_id:
            page = Page(order=len(chapter.pages) + 1)
            chapter.pages.append(page)
            return page

    raise HTTPException(status_code=404, detail="Chapter not found")


# --------------------------------------------------
# PANEL ENDPOINTS (STORY INTELLIGENCE LIVES HERE)
# --------------------------------------------------

@app.post(
    "/stories/{story_id}/chapters/{chapter_id}/pages/{page_id}/panels",
    response_model=Panel
)
def add_panel(
    story_id: str,
    chapter_id: str,
    page_id: str,
    story_beat: str,
    tension: int = 30
):
    """
    Add a panel to a page with narrative validation.
    """

    story = STORIES.get(story_id)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")

    for chapter in story.chapters:
        if chapter.id == chapter_id:
            for page in chapter.pages:
                if page.id == page_id:

                    # Enforce pacing progression
                    prev_tension = None
                    if page.panels:
                        prev_tension = page.panels[-1].tension

                    if not is_valid_progression(prev_tension, tension):
                        raise HTTPException(
                            status_code=400,
                            detail="Invalid narrative tension jump"
                        )

                    panel = Panel(
                        story_beat=story_beat,
                        tension=tension
                    )

                    page.panels.append(panel)
                    return panel

            raise HTTPException(status_code=404, detail="Page not found")

    raise HTTPException(status_code=404, detail="Chapter not found")

