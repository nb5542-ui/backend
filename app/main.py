from fastapi import FastAPI, HTTPException

from app.storybook import Storybook
from app.chapter import Chapter
from app.page import Page
from app.panel import Panel
from app.store import STORIES

from app.utils.beats import STORY_BEATS, is_valid_beat
from app.utils.pacing import is_valid_tension, is_valid_progression

app = FastAPI(title="AI Manga Story Engine", version="0.5.0")


# ----------------------------
# HEALTH
# ----------------------------

@app.get("/health")
def health():
    return {"status": "ok"}


# ----------------------------
# DISCOVERY
# ----------------------------

@app.get("/beats")
def list_beats():
    return sorted(STORY_BEATS)


# ----------------------------
# STORY
# ----------------------------

@app.post("/stories", response_model=Storybook)
def create_story():
    story = Storybook()
    STORIES[story.id] = story
    return story


@app.post("/stories/{story_id}/chapters", response_model=Chapter)
def add_chapter(story_id: str):
    story = STORIES.get(story_id)
    if not story:
        raise HTTPException(404, "Story not found")

    chapter = Chapter(order=len(story.chapters) + 1)
    story.chapters.append(chapter)
    return chapter


@app.post(
    "/stories/{story_id}/chapters/{chapter_id}/pages",
    response_model=Page
)
def add_page(story_id: str, chapter_id: str):
    story = STORIES.get(story_id)
    if not story:
        raise HTTPException(404, "Story not found")

    for chapter in story.chapters:
        if chapter.id == chapter_id:
            page = Page(order=len(chapter.pages) + 1)
            chapter.pages.append(page)
            return page

    raise HTTPException(404, "Chapter not found")


# ----------------------------
# PANEL (FINAL, SAFE VERSION)
# ----------------------------

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
    # ---- story lookup
    story = STORIES.get(story_id)
    if not story:
        raise HTTPException(404, "Story not found")

    # ---- VALIDATION (EXPLICIT & SAFE)
    if not is_valid_beat(story_beat):
        raise HTTPException(
            status_code=422,
            detail=f"Invalid story beat: {story_beat}"
        )

    if not is_valid_tension(tension):
        raise HTTPException(
            status_code=422,
            detail="Tension must be between 0 and 100"
        )

    for chapter in story.chapters:
        if chapter.id == chapter_id:
            for page in chapter.pages:
                if page.id == page_id:

                    prev = page.panels[-1].tension if page.panels else None
                    if not is_valid_progression(prev, tension):
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

    raise HTTPException(404, "Target not found")
