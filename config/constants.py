"""UI-related constants for Xenharmonic Voyager application."""

# ===== Calculation Parameters =====
MIN_NOTES_FOR_CALCULATION = 2
MAX_HISTORY_SIZE = 10
MAX_ROUGHNESS_FOR_PROGRESS = 2.0


# ===== Roughness Interpretation Thresholds =====
class RoughnessLevel:
    """Roughness level classification for consonance evaluation."""

    VERY_CONSONANT = 0.5
    CONSONANT = 1.0
    SLIGHTLY_CONSONANT = 2.0
    SLIGHTLY_DISSONANT = 4.0


# ===== UI Options =====
EDO_OPTIONS = [12, 19]
NUM_NOTES_OPTIONS = [2, 3, 4]
DEFAULT_NUM_NOTES = 3
OPTIMAL_COLS_THRESHOLD = 12
