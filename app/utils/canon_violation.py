from pydantic import BaseModel
from typing import List


class CanonViolation(BaseModel):
    panel_id: str
    canon_type: str  # character | relationship | world
    severity: str    # low | medium | high
    message: str
    confidence: float
    suggestion: str


def detect_canon_violations(story) -> List[CanonViolation]:
    violations: List[CanonViolation] = []

    canon = getattr(story, "canon", None)
    if not canon:
        return violations

    # ----------------------------------
    # CHARACTER CANON VIOLATIONS
    # ----------------------------------
    for chapter in story.chapters:
        for page in chapter.pages:
            for panel in page.panels:
                for char_id in panel.characters_present:
                    canon_char = canon.characters.get(char_id)

                    if canon_char and canon_char.alive is False:
                        violations.append(
                            CanonViolation(
                                panel_id=panel.id,
                                canon_type="character",
                                severity="high",
                                message=(
                                    f"Character '{char_id}' appears despite being marked dead"
                                ),
                                confidence=0.9,
                                suggestion=(
                                    "Consider adding a resurrection explanation, flashback, "
                                    "or revising canon state"
                                )
                            )
                        )

    # ----------------------------------
    # RELATIONSHIP CANON VIOLATIONS
    # ----------------------------------
    for key, rel in canon.relationships.items():
        if not rel.locked:
            continue

        char_a, char_b = key.split("|")

        for c in story.characters:
            if c.id != char_a:
                continue

            for r in c.relationships:
                if r.target_character_id != char_b:
                    continue

                if rel.status == "enemy" and r.trust > 0.6:
                    violations.append(
                        CanonViolation(
                            panel_id="unknown",
                            canon_type="relationship",
                            severity="medium",
                            message=(
                                f"Locked enemy relationship between {char_a} and {char_b} "
                                f"shows high trust"
                            ),
                            confidence=0.7,
                            suggestion=(
                                "Consider a reconciliation arc or unlock this relationship"
                            )
                        )
                    )

    return violations
