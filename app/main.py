from fastapi import FastAPI, HTTPException

from app.storybook import Storybook
from app.chapter import Chapter
from app.page import Page
from app.panel import Panel

from app.store import STORIES
from app.utils.beats import STORY_BEATS, recommend_beats
from app.utils.pacing import is_valid_progression


app = FastAPI(
    title="AI Manga Story Engine",
    version="0.3.0"
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/beats")
def list_story_beats():
    return sorted(STORY_BEATS)


@app.post("/stories", response_model=Storybook)
def create_story():
    story = Storybook()
    STORIES[story.id] = story
    return story


@app.get("/stories/{story_id}", response_model=Storybook)
def get_story(story_id: str):
    story = STORIES.get(story_id)
    if not story:
        raise HTTPException(404, "Story not found")
    return story


@app.put("/stories/{story_id}/intent")
def update_story_intent(story_id: str, intent: dict):
    story = STORIES.get(story_id)
    if not story:
        raise HTTPException(404, "Story not found")
    story.intent = story.intent.copy(update=intent)
    return story.intent


@app.get("/stories/{story_id}/intent")
def get_story_intent(story_id: str):
    story = STORIES.get(story_id)
    if not story:
        raise HTTPException(404, "Story not found")
    return story.intent


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
    story = STORIES.get(story_id)
    if not story:
        raise HTTPException(404, "Story not found")

    for chapter in story.chapters:
        if chapter.id == chapter_id:
            for page in chapter.pages:
                if page.id == page_id:

                    prev = page.panels[-1].tension if page.panels else None
                    if not is_valid_progression(prev, tension):
                        raise HTTPException(
                            400,
                            "Invalid narrative tension jump"
                        )

                    panel = Panel(
                        story_beat=story_beat,
                        tension=tension
                    )

                    page.panels.append(panel)
                    return panel

    raise HTTPException(404, "Target not found")


@app.post("/stories/{story_id}/beats/recommend")
def recommend_story_beats(story_id: str):
    story = STORIES.get(story_id)
    if not story:
        raise HTTPException(404, "Story not found")

    beats_used = []
    total_panels = 0

    for chapter in story.chapters:
        for page in chapter.pages:
            for panel in page.panels:
                beats_used.append(panel.story_beat)
                total_panels += 1

    story_progress = min(1.0, total_panels / 50)

    return {
        "story_progress": story_progress,
        "intent": story.intent,
        "recommended_beats": recommend_beats(
            story_progress,
            set(beats_used),
            story.intent.dict()
        )
    }
