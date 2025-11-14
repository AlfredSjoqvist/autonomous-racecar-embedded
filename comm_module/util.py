"""A collection of utilities."""


def clamp(val: int | float, low: int | float, high: int | float) -> int | float:
    """Clamp val between low and high."""
    return max(low, min(high, val))
