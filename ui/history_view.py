"""Observation history view component (View層)

このモジュールは、HistoryViewModelを受け取り、Streamlitで描画のみを行います。
ビジネスロジックは src/visualization/history_presenter.py に配置されています。
"""

import streamlit as st

from src.visualization.history_presenter import (
    HistoryViewModel,
    ObservationItemViewModel,
    pin_observation,
    unpin_observation,
)


def _render_observation_item(item: ObservationItemViewModel, key_suffix: str = "") -> None:
    """単一の観測アイテムを描画します。

    Args:
        item: 観測アイテムのViewModel
        key_suffix: ボタンキーの重複を避けるためのサフィックス
    """
    obs = item.obs
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

    with col1:
        st.markdown(f"**R = {obs.roughness:.6f}**")

    with col2:
        sorted_notes = sorted(obs.notes)
        notes_str = ", ".join(map(str, sorted_notes))
        st.caption(f"S = ({notes_str})")

    with col3:
        st.caption(f"{obs.edo}-EDO")

    with col4:
        if item.is_pinned:
            # 固定済み:解除ボタンを表示
            if st.button("📌🗑️", key=f"unpin{key_suffix}_{item.index}", help="Unpin"):
                unpin_observation(item.index)
                st.rerun()
        # 未固定:固定ボタンを表示
        elif st.button("📌", key=f"pin{key_suffix}_{item.index}", help="Pin"):
            pin_observation(obs)
            st.rerun()


def render_history_view(view_model: HistoryViewModel) -> None:
    """観測履歴を描画します。

    Args:
        view_model: Presenter層で準備されたHistoryViewModel
    """
    st.divider()
    st.markdown("### Observation History")
    st.caption("過去の観測結果を最大20件まで保存します。📌ボタンで固定。")

    if view_model.items:
        # 左右2列に分割: 左は最新10件、右は次の10件
        left_col, right_col = st.columns(2)

        # 左列: 最新10件 (インデックス0-9)
        with left_col:
            for item in view_model.items[:10]:
                _render_observation_item(item)

        # 右列: 次の10件 (インデックス10-19)
        with right_col:
            for item in view_model.items[10:20]:
                _render_observation_item(item, key_suffix="_old")
    else:
        st.caption("No observations yet")
