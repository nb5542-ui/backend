from fastapi import FastAPI, HTTPException
from app.storybook import Storybook
from app.store import STORIES

app = FastAPI(
    title="AI Manga Backend",
    version="0.1.0"
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


# -------------------------
# STORY ENDPOINTS
# -------------------------

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
    Get a story by ID.
    """
    if story_id not in STORIES:
        raise HTTPException(status_code=404, detail="Story not found")

    return STORIES[story_id]
