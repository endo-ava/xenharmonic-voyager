"""Xenharmonic Voyager - メインStreamlitアプリケーション

このモジュールは、Setharesの音響的ラフネスモデルを使用して、
異種調和の協和性を探求するためのユーザーインターフェースを提供します。
"""

import streamlit as st
from pydantic import ValidationError

from src.application.use_cases import CalculateConsonanceUseCase
from src.visualization.analysis_presenter import prepare_analysis_view_model
from src.visualization.dissonance_curve import prepare_dissonance_curve_view_model
from src.visualization.history_presenter import prepare_history_view_model
from ui.analysis_view import render_analysis_view
from ui.config.constants import STATE_EDO, STATE_NUM_NOTES, STATE_SELECTED_NOTES
from ui.dissonance_curve_view import render_dissonance_curve_view
from ui.help_sections import render_about_calculation, render_calculation_parameters
from ui.history_view import render_history_view
from ui.session_management import (
    get_observations_from_session,
    get_pinned_observations_from_session,
    record_observation_to_session,
)
from ui.setup import initialize_session, setup_page
from ui.sidebar import render_sidebar
from ui.step_selector import render_selection_status, render_step_selector

# ===== Setup & Initialize =====
setup_page()
initialize_session()

# ===== Header =====
st.title("Xenharmonic Voyager")
st.markdown(
    """
    Setharesの音響的ラフネスモデルを使用して、さまざまなチューニングシステムにおける協和性を探求します。
    ラフネス値が低いほど、協和性が高いことを示します。
    """
)

# ===== Controls =====
edo, num_notes = render_sidebar()
render_step_selector(edo, st.session_state[STATE_SELECTED_NOTES], num_notes)
render_selection_status(edo, st.session_state[STATE_SELECTED_NOTES])

# ===== Analysis =====
if len(st.session_state[STATE_SELECTED_NOTES]) == num_notes:
    try:
        # Calculate consonance
        use_case = CalculateConsonanceUseCase()
        result = use_case.execute(
            edo=st.session_state[STATE_EDO],
            notes=st.session_state[STATE_SELECTED_NOTES],
            include_pair_details=True,
        )

        # Prepare ViewModels
        analysis_vm = prepare_analysis_view_model(result.total_roughness)
        dissonance_vm = prepare_dissonance_curve_view_model(result.pair_details)

        # Render analysis results
        render_analysis_view(analysis_vm)

        st.divider()
        with st.expander("Dissonance Curve Visualization", expanded=True):
            render_dissonance_curve_view(dissonance_vm)

        # Record and render history
        record_observation_to_session(
            st.session_state[STATE_EDO],
            st.session_state[STATE_SELECTED_NOTES],
            result.total_roughness,
        )
        history_vm = prepare_history_view_model(
            get_observations_from_session(),
            get_pinned_observations_from_session(),
        )
        render_history_view(history_vm)

    except ValidationError as e:
        st.error(f"Validation Error: {e}")
    except Exception as e:
        st.error(f"Calculation Error: {e}")

# ===== Help Sections =====
st.divider()
render_calculation_parameters(
    st.session_state[STATE_EDO],
    st.session_state[STATE_SELECTED_NOTES],
    st.session_state[STATE_NUM_NOTES],
)
render_about_calculation()

# ===== Footer =====
st.divider()
st.caption(
    """
    **Xenharmonic Voyager** - 12-EDOを超えたチューニングシステムの探求
    Streamlitで構築 | Setharesのラフネスモデル (1993) を利用
    """
)
