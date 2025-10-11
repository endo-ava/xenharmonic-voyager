"""Observation history view component."""

import streamlit as st

from config.constants import MAX_HISTORY_SIZE


def record_observation(edo: int, notes: list[int], roughness: float) -> None:
    """Record observation to history.

    Args:
        edo: EDO value
        notes: Selected note indices
        roughness: Calculated roughness value
    """
    current_observation = {
        "edo": edo,
        "notes": tuple(notes),
        "roughness": roughness,
    }

    history = st.session_state.observation_history
    # 履歴の最後と同じでなければ追加
    if not history or history[-1] != current_observation:
        history.append(current_observation)
        # 最大件数に制限
        if len(history) > MAX_HISTORY_SIZE:
            history.pop(0)


def get_all_observations() -> list[dict]:
    """Get all observations (pinned + history).

    Returns:
        list[dict]: Combined list of pinned and unpinned observations
    """
    pinned = [
        {"obs": obs, "is_pinned": True, "pin_idx": idx}
        for idx, obs in enumerate(st.session_state.pinned_observations)
    ]
    unpinned = [
        {"obs": obs, "is_pinned": False, "history_idx": idx}
        for idx, obs in enumerate(reversed(st.session_state.observation_history))
        if obs not in st.session_state.pinned_observations
    ]
    return pinned + unpinned


def render_history_view() -> None:
    """Render observation history with pin/unpin functionality."""
    st.divider()
    st.markdown("### Observation History")

    all_observations = get_all_observations()

    if all_observations:
        for item in all_observations:
            obs = item["obs"]
            col1, col2, col3, col4 = st.columns([2, 3, 2, 1])

            with col1:
                st.code(f"R = {obs['roughness']:.6f}", language=None)

            with col2:
                sorted_notes = sorted(obs["notes"])
                notes_str = ", ".join(map(str, sorted_notes))
                st.caption(f"S = ({notes_str})")

            with col3:
                st.caption(f"{obs['edo']}-EDO")

            with col4:
                if item["is_pinned"]:
                    # 固定済み:解除ボタンを表示
                    if st.button("📌🗑️", key=f"unpin_{item['pin_idx']}", help="Unpin"):
                        st.session_state.pinned_observations.pop(item["pin_idx"])
                        st.rerun()
                # 未固定:固定ボタンを表示
                elif st.button("📌", key=f"pin_{item['history_idx']}", help="Pin"):
                    st.session_state.pinned_observations.append(obs)
                    st.rerun()
    else:
        st.caption("No observations yet")
