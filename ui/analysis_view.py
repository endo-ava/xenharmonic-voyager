"""Roughness analysis view component (View層)

このモジュールは、AnalysisViewModelを受け取り、Streamlitで描画のみを行います。
ビジネスロジックは src/visualization/analysis_presenter.py に配置されています。
"""

import streamlit as st

from src.visualization.analysis_presenter import AnalysisViewModel


def render_analysis_view(view_model: AnalysisViewModel) -> None:
    """ラフネス解析結果を描画します。

    Args:
        view_model: Presenter層で準備されたAnalysisViewModel
    """
    st.divider()
    st.markdown("### Roughness Analysis")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.metric(
            label="R(S)",
            value=f"{view_model.roughness:.6f}",
            help="音響的ラフネス関数の値。値が小さいほど協和的。",
        )

    with col2:
        st.caption(f"Consonance Level: {view_model.roughness_level}")
        st.progress(view_model.inverted_progress)
