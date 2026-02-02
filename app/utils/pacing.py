MAX_TENSION_JUMP = 30


def is_valid_tension(value: int) -> bool:
    return 0 <= value <= 100


def is_valid_progression(prev: int | None, current: int) -> bool:
    if prev is None:
        return True
    return abs(current - prev) <= MAX_TENSION_JUMP
