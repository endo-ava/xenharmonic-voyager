"""Sidebar component for parameter selection."""

import streamlit as st

from config.constants import DEFAULT_NUM_NOTES, EDO_OPTIONS, NUM_NOTES_OPTIONS


def render_sidebar() -> tuple[int, int]:
    """Render sidebar with EDO and number of notes selection.

    Returns:
        tuple[int, int]: Selected EDO and number of notes
    """
    with st.sidebar:
        st.header("Parameters")

        # EDO selection
        new_edo = st.selectbox(
            "N-EDO",
            options=EDO_OPTIONS,
            index=0,
            format_func=lambda x: f"{x}",
            help="分析対象とする平均率のNを選択します。",
        )

        st.caption(f"Frequency ratio: 2^(k/{new_edo}), k ∈ [0, {new_edo})")

        # EDO変更時: 選択音をクリア
        if new_edo != st.session_state.edo:
            st.session_state.edo = new_edo
            st.session_state.selected_notes = []

        st.divider()

        # Number of steps selection
        new_num_notes = st.selectbox(
            "Number of Steps to Analyze",
            options=NUM_NOTES_OPTIONS,
            index=NUM_NOTES_OPTIONS.index(DEFAULT_NUM_NOTES),
            help="協和度を計算する音の数を選択します。",
        )

        # 構成音数変更時: 選択音を調整
        if new_num_notes != st.session_state.num_notes:
            st.session_state.num_notes = new_num_notes
            if len(st.session_state.selected_notes) > new_num_notes:
                st.session_state.selected_notes = st.session_state.selected_notes[:new_num_notes]

    return new_edo, new_num_notes
