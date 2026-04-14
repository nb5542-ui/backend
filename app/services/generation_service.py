import random

from streamlit import context


def mock_llm_response(context: dict):
    """
    Context-aware mock generation
    """

    characters = context.get("character_context", [])
    scene = context.get("scene_context", {})
    narrative = context.get("narrative_state", {})

    # Pick first character (for now)
    character_name = characters[0]["name"] if characters else "Someone"

    location = scene.get("location", "unknown place")
    atmosphere = scene.get("atmosphere", "neutral")

    emotion = narrative.get("emotional_drift", {}).get(character_name, "neutral")

    # Basic logic
    text = f"{character_name} stands in {location}, feeling {emotion}."
    mood = atmosphere or "neutral"

    return {
        "text": text,
        "mood": mood
    }


def normalize_panel_output(raw: dict, context: dict):

    characters = context.get("character_context", [])

    if characters and len(characters) > 0:
        character_id = characters[0].get("id", "char_1")
    else:
        character_id = "char_1"

    panel_context = context.get("panel_context", {})

    return {
        "panel": {
            "type": panel_context.get("panel_type", "dialogue"),

            "dialogue": [
                {
                    "character_id": character_id,
                    "text": raw.get("text", ""),
                    "tone": raw.get("mood", "neutral")
                }
            ],

            "action": {
                "description": raw.get("text", ""),
                "intensity": "medium"
            },

            "emotion": {
                "primary": raw.get("mood", "neutral"),
                "secondary": "focused"
            },

            "visual": {
                "characters": [
                    {
                        "id": character_id,
                        "pose": "standing",
                        "expression": raw.get("mood", "neutral")
                    }
                ],
                "environment": context.get("scene_context", {}).get("location", "unknown"),
                "lighting": "dramatic",
                "mood": raw.get("mood", "neutral")
            },

            "camera": {
                "shot_type": "medium",
                "angle": "eye-level",
                "focus": "character"
            }
        }
    }


def generate_panel(context: dict):
    """
    Main entry point
    """

    raw_output = mock_llm_response(context)

    structured_output = normalize_panel_output(raw_output, context)

    return structured_output