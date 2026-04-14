import random


def mock_llm_response(context: dict):
    """
    Temporary mock instead of real AI
    """

    return {
        "text": "Ryu looks at the enemy and speaks with intensity.",
        "mood": "tense"
    }


def normalize_panel_output(raw: dict, context: dict):
    """
    Converts flexible AI output → strict panel schema
    """

    panel_context = context.get("panel_context", {})

    return {
        "panel": {
            "type": panel_context.get("panel_type", "dialogue"),

            "dialogue": [
                {
                    "character_id": "char_1",
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
                        "id": "char_1",
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