from typing import List, Dict
from pydantic import BaseModel


class SceneWarning(BaseModel):
    panel_id: str
    scene_id: str
    location: str
    message: str
    severity: str  # low | medium


def assign_scene(panel, previous_panel):
    """
    Decide whether to continue the scene or start a new one.
    """

    if not previous_panel:
        panel.scene_id = "scene_1"
        return

    # inherit location if not provided
    if panel.location is None:
        panel.location = previous_panel.location

    # same location → same scene
    if panel.location == previous_panel.location:
        panel.scene_id = previous_panel.scene_id
    else:
        # new scene
        prev_scene_num = int(previous_panel.scene_id.split("_")[1])
        panel.scene_id = f"scene_{prev_scene_num + 1}"


def detect_scene_warnings(story) -> List[SceneWarning]:
    warnings: List[SceneWarning] = []

    last_location_by_character: Dict[str, str] = {}

    all_panels = []
    for chapter in story.chapters:
        for page in chapter.pages:
            for panel in page.panels:
                all_panels.append(panel)

    for panel in all_panels:
        for char_id in panel.characters_present:
            prev_loc = last_location_by_character.get(char_id)

            if prev_loc and prev_loc != panel.location:
                warnings.append(
                    SceneWarning(
                        panel_id=panel.id,
                        scene_id=panel.scene_id,
                        location=panel.location,
                        message=(
                            f"Character {char_id} appears in "
                            f"{panel.location} without transition from {prev_loc}"
                        ),
                        severity="medium"
                    )
                )

            last_location_by_character[char_id] = panel.location

    return warnings
