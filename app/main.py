from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.storybook import Storybook
from app.chapter import Chapter
from app.page import Page
from app.panel import Panel, PanelCreate
from app.character import Character, Relationship

from app.store import STORIES

from app.utils.beats import STORY_BEATS
from app.utils.pacing import is_valid_progression
from app.utils.emotion_drift import compute_emotional_drift
from app.utils.relationship_drift import compute_relationship_drift
from app.utils.scene_tracking import assign_scene, detect_scene_warnings
from app.utils.story_intent import StoryIntent
from app.utils.intent_timeline import build_intent_timeline
from app.utils.beat_explanation import explain_beat


app = FastAPI(
    title="AI Manga Story Engine",
    version="0.8.1"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ==================================================
# REQUEST MODELS
# ==================================================

class CreateStoryRequest(BaseModel):
    title: str


# ==================================================
# HEALTH
# ==================================================

@app.get("/health")
def health_check():
    return {"status": "ok"}

# =========================================
# GENERATE (NEW)
# =========================================

@app.post("/generate")
async def generate(data: dict):
    print("RECEIVED DATA:", data)

    return {
        "status": "success",
        "message": "generation pipeline working",
        "panel": data.get("panel_context", {})
    }


# ==================================================
# DISCOVERY
# ==================================================

@app.get("/beats")
def list_story_beats():
    return sorted(STORY_BEATS)


# ==================================================
# STORY
# ==================================================

@app.post("/stories", response_model=Storybook)
def create_story(payload: CreateStoryRequest):
    story = Storybook(title=payload.title)
    STORIES[story.id] = story
    return story


@app.get("/stories/{story_id}", response_model=Storybook)
def get_story(story_id: str):
    story = STORIES.get(story_id)
    if not story:
        raise HTTPException(404, "Story not found")
    return story


# ==================================================
# STORY INTENT
# ==================================================

@app.post("/stories/{story_id}/intent")
def set_story_intent(story_id: str, intent: StoryIntent):
    story = STORIES.get(story_id)
    if not story:
        raise HTTPException(404, "Story not found")

    story.intent = intent
    return {
        "message": "Story intent set successfully",
        "intent": intent
    }


# ==================================================
# CHARACTERS
# ==================================================

@app.post("/stories/{story_id}/characters", response_model=Character)
def add_character(story_id: str, character: Character):
    story = STORIES.get(story_id)
    if not story:
        raise HTTPException(404, "Story not found")

    story.characters.append(character)
    return character


@app.get("/stories/{story_id}/characters", response_model=list[Character])
def list_characters(story_id: str):
    story = STORIES.get(story_id)
    if not story:
        raise HTTPException(404, "Story not found")

    return story.characters


# ==================================================
# CHAPTERS
# ==================================================

@app.post("/stories/{story_id}/chapters", response_model=Chapter)
def add_chapter(story_id: str):
    story = STORIES.get(story_id)
    if not story:
        raise HTTPException(404, "Story not found")

    chapter = Chapter(order=len(story.chapters) + 1)
    story.chapters.append(chapter)
    return chapter


# ==================================================
# PAGES
# ==================================================

@app.post("/stories/{story_id}/chapters/{chapter_id}/pages", response_model=Page)
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


# ==================================================
# PANELS (CORE ENGINE LOGIC)
# ==================================================

@app.post(
    "/stories/{story_id}/chapters/{chapter_id}/pages/{page_id}/panels",
    response_model=Panel
)
def add_panel(
    story_id: str,
    chapter_id: str,
    page_id: str,
    payload: PanelCreate
):
    story = STORIES.get(story_id)
    if not story:
        raise HTTPException(404, "Story not found")

    for chapter in story.chapters:
        if chapter.id == chapter_id:
            for page in chapter.pages:
                if page.id == page_id:

                    prev_tension = page.panels[-1].tension if page.panels else None
                    if not is_valid_progression(prev_tension, payload.tension):
                        raise HTTPException(
                            status_code=400,
                            detail="Invalid narrative tension jump"
                        )

                    panel = Panel(**payload.model_dump())

                    # Scene awareness
                    previous_panel = page.panels[-1] if page.panels else None
                    assign_scene(panel, previous_panel)

                    page.panels.append(panel)

                    # Emotional drift
                    for character in story.characters:
                        if character.id in panel.characters_present:
                            character.emotional_state = compute_emotional_drift(
                                current_state=character.emotional_state,
                                story_beat=panel.story_beat,
                                tension=panel.tension,
                                is_focus=(character.id == panel.focus_character)
                            )

                    # Relationship drift
                    present_ids = panel.characters_present
                    for source in story.characters:
                        if source.id not in present_ids:
                            continue

                        for target in story.characters:
                            if target.id == source.id or target.id not in present_ids:
                                continue

                            rel = next(
                                (
                                    r for r in source.relationships
                                    if r.target_character_id == target.id
                                ),
                                None
                            )

                            if not rel:
                                rel = Relationship(target_character_id=target.id)
                                source.relationships.append(rel)

                            updated = compute_relationship_drift(
                                current={
                                    "trust": rel.trust,
                                    "hostility": rel.hostility,
                                    "familiarity": rel.familiarity
                                },
                                story_beat=panel.story_beat,
                                tension=panel.tension,
                                is_focus=(source.id == panel.focus_character)
                            )

                            rel.trust = updated["trust"]
                            rel.hostility = updated["hostility"]
                            rel.familiarity = updated["familiarity"]

                    return panel

    raise HTTPException(404, "Page not found")


# ==================================================
# DEBUG / INSPECTION
# ==================================================

@app.get("/stories/{story_id}/characters/{character_id}/emotion")
def get_character_emotion(story_id: str, character_id: str):
    story = STORIES.get(story_id)
    if not story:
        raise HTTPException(404, "Story not found")

    character = story.get_character(character_id)
    if not character:
        raise HTTPException(404, "Character not found")

    return character.emotional_state


@app.get("/stories/{story_id}/characters/{character_id}/relationships")
def get_character_relationships(story_id: str, character_id: str):
    story = STORIES.get(story_id)
    if not story:
        raise HTTPException(404, "Story not found")

    character = story.get_character(character_id)
    if not character:
        raise HTTPException(404, "Character not found")

    return character.relationships


# ==================================================
# SCENE WARNINGS
# ==================================================

@app.get("/stories/{story_id}/scene-warnings")
def get_scene_warnings(story_id: str):
    story = STORIES.get(story_id)
    if not story:
        raise HTTPException(404, "Story not found")

    return detect_scene_warnings(story)


# ==================================================
# INTENT DRIFT TIMELINE
# ==================================================

@app.get("/stories/{story_id}/intent-timeline")
def get_intent_timeline(story_id: str):
    story = STORIES.get(story_id)
    if not story:
        raise HTTPException(404, "Story not found")

    if not story.intent:
        return {
            "message": "No intent defined for this story",
            "timeline": []
        }

    return build_intent_timeline(story)


# ==================================================
# BEAT EXPLANATION
# ==================================================

@app.get("/stories/{story_id}/panels/{panel_id}/beat-explanation")
def get_beat_explanation(story_id: str, panel_id: str):
    story = STORIES.get(story_id)
    if not story:
        raise HTTPException(404, "Story not found")

    panel = story.find_panel(panel_id)
    if not panel:
        raise HTTPException(404, "Panel not found")

    return explain_beat(story, panel)
