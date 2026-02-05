from fastapi import FastAPI, HTTPException

from app.storybook import Storybook
from app.utils.character_arc import analyze_character_arc
from app.utils.beat_explanation import explain_beat


from app.chapter import Chapter
from app.page import Page
from app.panel import Panel, PanelCreate
from app.utils.intent_drift import analyze_intent_drift

from app.character import Character, Relationship

from app.store import STORIES
from app.utils.beats import STORY_BEATS
from app.utils.pacing import is_valid_progression
from app.utils.emotion_drift import compute_emotional_drift
from app.utils.relationship_drift import compute_relationship_drift


app = FastAPI(
    title="AI Manga Story Engine",
    version="0.5.0"
)

# --------------------------------------------------
# HEALTH
# --------------------------------------------------

@app.get("/health")
def health_check():
    return {"status": "ok"}


# --------------------------------------------------
# DISCOVERY
# --------------------------------------------------

@app.get("/beats")
def list_story_beats():
    return sorted(STORY_BEATS)


# --------------------------------------------------
# STORY
# --------------------------------------------------

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


# --------------------------------------------------
# CHARACTERS
# --------------------------------------------------

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


# --------------------------------------------------
# CHAPTERS
# --------------------------------------------------

@app.post("/stories/{story_id}/chapters", response_model=Chapter)
def add_chapter(story_id: str):
    story = STORIES.get(story_id)
    if not story:
        raise HTTPException(404, "Story not found")

    chapter = Chapter(order=len(story.chapters) + 1)
    story.chapters.append(chapter)
    return chapter


# --------------------------------------------------
# PAGES
# --------------------------------------------------

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


# --------------------------------------------------
# PANELS (EMOTION + RELATIONSHIP DRIFT)
# --------------------------------------------------

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

                    prev_tension = (
                        page.panels[-1].tension if page.panels else None
                    )

                    if not is_valid_progression(prev_tension, payload.tension):
                        raise HTTPException(
                            status_code=400,
                            detail="Invalid narrative tension jump"
                        )

                    panel = Panel(**payload.model_dump())
                    page.panels.append(panel)

                    # -----------------------------
                    # STEP 3 — EMOTIONAL DRIFT
                    # -----------------------------
                    for character in story.characters:
                        if character.id in panel.characters_present:
                            character.emotional_state = compute_emotional_drift(
                                current_state=character.emotional_state,
                                story_beat=panel.story_beat,
                                tension=panel.tension,
                                is_focus=(character.id == panel.focus_character)
                            )

                    # -----------------------------
                    # STEP 4 — RELATIONSHIP DRIFT
                    # -----------------------------
                    present_ids = panel.characters_present

                    for source in story.characters:
                        if source.id not in present_ids:
                            continue

                        for target in story.characters:
                            if target.id == source.id or target.id not in present_ids:
                                continue

                            rel = next(
                                (r for r in source.relationships
                                 if r.target_character_id == target.id),
                                None
                            )

                            if not rel:
                                rel = Relationship(
                                    target_character_id=target.id
                                )
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


# --------------------------------------------------
# DEBUG / INSPECTION
# --------------------------------------------------

@app.get("/stories/{story_id}/characters/{character_id}/emotion")
def get_character_emotion(story_id: str, character_id: str):
    story = STORIES.get(story_id)
    if not story:
        raise HTTPException(404, "Story not found")

    for character in story.characters:
        if character.id == character_id:
            return character.emotional_state

    raise HTTPException(404, "Character not found")


@app.get("/stories/{story_id}/characters/{character_id}/relationships")
def get_character_relationships(story_id: str, character_id: str):
    story = STORIES.get(story_id)
    if not story:
        raise HTTPException(404, "Story not found")

    for character in story.characters:
        if character.id == character_id:
            return character.relationships

    raise HTTPException(404, "Character not found")
@app.get("/stories/{story_id}/intent-drift")
def get_intent_drift(story_id: str):
    story = STORIES.get(story_id)
    if not story:
        raise HTTPException(404, "Story not found")

    return analyze_intent_drift(story)
# --------------------------------------------------
# CHARACTER ARC (STEP 5)
# --------------------------------------------------

@app.get("/stories/{story_id}/characters/{character_id}/arc")
def get_character_arc(story_id: str, character_id: str):
    story = STORIES.get(story_id)
    if not story:
        raise HTTPException(404, "Story not found")

    return analyze_character_arc(story, character_id)
# --------------------------------------------------
# BEAT EXPLANATION (STEP 6)
# --------------------------------------------------

@app.get(
    "/stories/{story_id}/chapters/{chapter_id}/pages/{page_id}/panels/{panel_id}/explain"
)
def explain_panel_beat(
    story_id: str,
    chapter_id: str,
    page_id: str,
    panel_id: str
):
    story = STORIES.get(story_id)
    if not story:
        raise HTTPException(404, "Story not found")

    for chapter in story.chapters:
        if chapter.id != chapter_id:
            continue
        for page in chapter.pages:
            if page.id != page_id:
                continue
            for panel in page.panels:
                if panel.id == panel_id:
                    return explain_beat(story, panel)

    raise HTTPException(404, "Panel not found")



