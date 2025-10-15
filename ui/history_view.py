"""Observation history view component."""

from typing import Any, cast

import streamlit as st

from config.constants import (
    MAX_HISTORY_SIZE,
    STATE_OBSERVATION_HISTORY,
    STATE_PINNED_OBSERVATIONS,
)
from ui.models import Observation


def record_observation(edo: int, notes: list[int], roughness: float) -> None:
    """Record observation to history.

    Args:
        edo: EDO value
        notes: Selected note indices
        roughness: Calculated roughness value
    """
    current_observation = Observation(edo=edo, notes=tuple(notes), roughness=roughness)

    history = st.session_state[STATE_OBSERVATION_HISTORY]
    # 履歴の最後と同じでなければ追加
    if not history or history[-1] != current_observation:
        history.append(current_observation)
        # 最大件数に制限
        if len(history) > MAX_HISTORY_SIZE:
            history.pop(0)


def get_all_observations() -> list[dict[str, Any]]:
    """Get all observations (pinned + history).

    Returns:
        list[dict]: Combined list of pinned and unpinned observations
    """
    pinned = [
        {"obs": obs, "is_pinned": True, "pin_idx": idx}
        for idx, obs in enumerate(st.session_state[STATE_PINNED_OBSERVATIONS])
    ]
    # Use set for O(1) lookup performance
    pinned_set = set(st.session_state[STATE_PINNED_OBSERVATIONS])
    unpinned = [
        {"obs": obs, "is_pinned": False, "history_idx": idx}
        for idx, obs in enumerate(reversed(st.session_state[STATE_OBSERVATION_HISTORY]))
        if obs not in pinned_set
    ]
    return pinned + unpinned


def _render_observation_item(item: dict[str, Any], key_suffix: str = "") -> None:
    """Render a single observation item.

    Args:
        item: Observation item with 'obs', 'is_pinned', and optional 'pin_idx'/'history_idx'
        key_suffix: Suffix to add to button keys to avoid duplicates
    """
    obs = cast(Observation, item["obs"])
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
        if item["is_pinned"]:
            # 固定済み:解除ボタンを表示
            if st.button("📌🗑️", key=f"unpin{key_suffix}_{item['pin_idx']}", help="Unpin"):
                st.session_state[STATE_PINNED_OBSERVATIONS].pop(item["pin_idx"])
                st.rerun()
        # 未固定:固定ボタンを表示
        elif st.button("📌", key=f"pin{key_suffix}_{item['history_idx']}", help="Pin"):
            st.session_state[STATE_PINNED_OBSERVATIONS].append(obs)
            st.rerun()


def render_history_view() -> None:
    """Render observation history with pin/unpin functionality."""
    st.divider()
    st.markdown("### Observation History")
    st.caption("過去の観測結果を最大20件まで保存します。📌ボタンで固定。")

    all_observations = get_all_observations()

    if all_observations:
        # 左右2列に分割: 左は最新10件、右は次の10件
        left_col, right_col = st.columns(2)

        # 左列: 最新10件 (インデックス0-9)
        with left_col:
            for item in all_observations[:10]:
                _render_observation_item(item)

        # 右列: 次の10件 (インデックス10-19)
        with right_col:
            for item in all_observations[10:20]:
                _render_observation_item(item, key_suffix="_old")
    else:
        st.caption("No observations yet")
