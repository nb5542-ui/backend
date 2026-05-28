import random

from streamlit import context
from openai import OpenAI
from app.schemas.panel_schema import Panel
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))



def call_openai(context: dict):

    prompt = f"""
    You are a professional manga panel generator.

    Context:
    {context}

    Generate a complete panel.
    """

    panel_tool = {
        "type": "function",
        "function": {
            "name": "generate_panel",
            "description": "Generate a structured manga panel",
            "parameters": Panel.model_json_schema()
        }
    }

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You must output ONLY via the provided function. No text."
            },
            {"role": "user", "content": prompt}
        ],
        tools=[panel_tool],
        tool_choice={
            "type": "function",
            "function": {"name": "generate_panel"}
        }
    )

    tool_call = response.choices[0].message.tool_calls[0]

    raw_json = tool_call.function.arguments

    # ✅ Strict validation (no parsing hacks)
    panel = Panel.model_validate_json(raw_json)

    return panel 


def normalize_panel_output(panel: Panel, context: dict):

    characters = context.get("character_context", [])
    panel_context = context.get("panel_context", {})

    # Map character names → IDs
    name_to_id = {
        c.get("name"): c.get("id")
        for c in characters
    }

    def resolve_character_id(name):
        return name_to_id.get(name, "char_1")

    # ✅ Dialogue
    dialogue = [
        {
            "character_id": resolve_character_id(d.speaker),
            "text": d.text,
            "tone": "neutral"  # can later map from emotion layer
        }
        for d in panel.dialogue
    ]

    # ✅ Action
    action = [
        {
            "description": a.description,
            "intensity": "medium"
        }
        for a in panel.action
    ]

    # ✅ Emotion (convert list → primary/secondary)
    primary_emotion = panel.emotion[0].emotion if panel.emotion else "neutral"

    emotion = {
        "primary": primary_emotion,
        "secondary": "focused"
    }

    # ✅ Visual
    visual_characters = [
        {
            "id": resolve_character_id(name),
            "pose": "dynamic",  # let AI drive later
            "expression": primary_emotion
        }
        for name in panel.visual.characters
    ]

    visual = {
        "characters": visual_characters,
        "environment": panel.visual.setting,
        "details": panel.visual.details,
        "lighting": "cinematic",  # keep default but better wording
        "mood": primary_emotion
    }

    # ✅ Camera
    camera = {
        "shot_type": panel.camera.shot_type,
        "angle": panel.camera.angle,
        "focus": "character"
    }

    return {
        "panel": {
            "type": panel_context.get("panel_type", "dialogue"),
            "dialogue": dialogue,
            "action": action,
            "emotion": emotion,
            "visual": visual,
            "camera": camera
        }
    }


def generate_panel(context: dict):

    raw_output = call_openai(context)  # 🔥 real AI now

    structured_output = normalize_panel_output(raw_output, context)

    return structured_output