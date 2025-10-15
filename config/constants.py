"""UI-related constants for Xenharmonic Voyager application."""

# ===== Calculation Parameters =====
MIN_NOTES_FOR_CALCULATION = 2
MAX_HISTORY_SIZE = 20
MAX_ROUGHNESS_FOR_PROGRESS = 2.0


# ===== Roughness Interpretation Thresholds =====
class RoughnessLevel:
    """Roughness level classification for consonance evaluation."""

    VERY_CONSONANT = 0.5
    CONSONANT = 1.0
    SLIGHTLY_CONSONANT = 2.0
    SLIGHTLY_DISSONANT = 4.0


# ===== UI Options =====
EDO_OPTIONS = [12, 19, 31, 41, 53]
NUM_NOTES_OPTIONS = [2, 3, 4, 5]
DEFAULT_NUM_NOTES = 3
OPTIMAL_COLS_THRESHOLD = 12
STEP_SELECTOR_WIDE_COLS = 21  # Number of columns for large EDOs


# ===== Session State Keys =====
STATE_EDO = "edo"
STATE_NUM_NOTES = "num_notes"
STATE_SELECTED_NOTES = "selected_notes"
STATE_REFERENCE_SCORE = "reference_score"
STATE_MAX_SCORE = "max_score"
STATE_OBSERVATION_HISTORY = "observation_history"
STATE_PINNED_OBSERVATIONS = "pinned_observations"


# ===== Reference Chords =====
REF_CHORD_MAJOR_TRIAD = [0, 4, 7]  # 12-EDO major triad
REF_CHORD_MINOR_SECOND = [0, 1]  # 12-EDO minor second (maximum dissonance)


# ===== Selection Indicator Colors =====
SELECTION_COLORS = ["🔴", "🟡", "🟢", "🔵", "🟣", "🟠"]
UNSELECTED_COLOR = "⚪"
