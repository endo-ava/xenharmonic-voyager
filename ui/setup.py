"""Application setup and initialization for Xenharmonic Voyager.

このモジュールは、Streamlitアプリケーションの起動処理を担当します:
- ページ設定
- CSS適用
- セッション状態の初期化
- 参照スコアの計算
"""

import streamlit as st

from src.application.use_cases import CalculateConsonanceUseCase
from ui.config.constants import (
    REF_CHORD_MAJOR_TRIAD,
    REF_CHORD_MINOR_SECOND,
    STATE_EDO,
    STATE_MAX_SCORE,
    STATE_NUM_NOTES,
    STATE_OBSERVATION_HISTORY,
    STATE_PINNED_OBSERVATIONS,
    STATE_REFERENCE_SCORE,
    STATE_SELECTED_NOTES,
)
from ui.config.styles import CUSTOM_CSS


def setup_page() -> None:
    """Configure Streamlit page settings and apply custom CSS."""
    st.set_page_config(
        page_title="Xenharmonic Voyager",
        page_icon="🎵",
        layout="wide",
    )
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def initialize_session() -> None:
    """Initialize session state and calculate reference scores.

    This function:
    1. Initializes session state with default values
    2. Clears legacy dict-based observations (force reset)
    3. Calculates reference scores (major triad and minor second) once at startup
    """
    # Initialize session state with defaults
    defaults = {
        STATE_EDO: 12,
        STATE_NUM_NOTES: 3,
        STATE_SELECTED_NOTES: [],
        STATE_REFERENCE_SCORE: None,
        STATE_MAX_SCORE: None,
        STATE_OBSERVATION_HISTORY: [],
        STATE_PINNED_OBSERVATIONS: [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # Clear legacy dict-based observations (force reset)
    if st.session_state[STATE_OBSERVATION_HISTORY] and any(
        isinstance(obs, dict) for obs in st.session_state[STATE_OBSERVATION_HISTORY]
    ):
        st.session_state[STATE_OBSERVATION_HISTORY] = []
        st.session_state[STATE_PINNED_OBSERVATIONS] = []

    # Calculate reference scores at startup (once only)
    use_case = CalculateConsonanceUseCase()

    if st.session_state[STATE_REFERENCE_SCORE] is None:
        result = use_case.execute(
            edo=12,
            notes=REF_CHORD_MAJOR_TRIAD,
        )
        st.session_state[STATE_REFERENCE_SCORE] = result.total_roughness

    if st.session_state[STATE_MAX_SCORE] is None:
        result = use_case.execute(
            edo=12,
            notes=REF_CHORD_MINOR_SECOND,
        )
        st.session_state[STATE_MAX_SCORE] = result.total_roughness
