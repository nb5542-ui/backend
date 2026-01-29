from fastapi import FastAPI, HTTPException

from app.storybook import Storybook
from app.chapter import Chapter
from app.page import Page
from app.panel import Panel
from app.store import STORIES


app = FastAPI(
    title="AI Manga Backend",
    version="0.1.0"
)

# --------------------------------------------------
# HEALTH
# --------------------------------------------------

@app.get("/health")
def health_check():
    return {"status": "ok"}


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

    chapter = Chapter(order=len(story.chapters) + 1)
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
# PANEL ENDPOINTS
# --------------------------------------------------

@app.post(
    "/stories/{story_id}/chapters/{chapter_id}/pages/{page_id}/panels",
    response_model=Panel
)
def add_panel(story_id: str, chapter_id: str, page_id: str):
    """
    Add a panel to a page.
    """
    story = STORIES.get(story_id)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")

    for chapter in story.chapters:
        if chapter.id == chapter_id:
            for page in chapter.pages:
                if page.id == page_id:
                    panel = Panel()
                    page.panels.append(panel)
                    return panel

            raise HTTPException(status_code=404, detail="Page not found")

    raise HTTPException(status_code=404, detail="Chapter not found")


