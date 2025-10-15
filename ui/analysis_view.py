"""Roughness analysis view component."""

import streamlit as st

from config.constants import MAX_ROUGHNESS_FOR_PROGRESS, RoughnessLevel


def get_roughness_level(roughness: float) -> str:
    """Get consonance level from roughness value.

    Args:
        roughness: Roughness value to classify

    Returns:
        str: Consonance level label
    """
    levels = [
        (RoughnessLevel.VERY_CONSONANT, "L1 (Very Consonant)"),
        (RoughnessLevel.CONSONANT, "L2 (Consonant)"),
        (RoughnessLevel.SLIGHTLY_CONSONANT, "L3 (Slightly Consonant)"),
        (RoughnessLevel.SLIGHTLY_DISSONANT, "L4 (Slightly Dissonant)"),
    ]
    return next(
        (label for threshold, label in levels if roughness < threshold),
        "L5 (Dissonant)",
    )


def calculate_inverted_progress(
    roughness: float,
    max_roughness: float = MAX_ROUGHNESS_FOR_PROGRESS,
) -> float:
    """Convert roughness value to inverted progress bar value (smaller = longer bar).

    Args:
        roughness: Roughness value
        max_roughness: Maximum roughness value for progress calculation

    Returns:
        float: Progress value between 0.0 and 1.0
    """
    return max(0.0, min(1.0, (max_roughness - roughness) / max_roughness))


def render_analysis_view(roughness: float) -> None:
    """Render roughness analysis results.

    Args:
        roughness: Calculated roughness value
    """
    st.divider()
    st.markdown("### Roughness Analysis")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.metric(
            label="R(S)",
            value=f"{roughness:.6f}",
            help="音響的ラフネス関数の値。値が小さいほど協和的。",
        )

    with col2:
        level = get_roughness_level(roughness)
        st.caption(f"Consonance Level: {level}")
        st.progress(calculate_inverted_progress(roughness))
