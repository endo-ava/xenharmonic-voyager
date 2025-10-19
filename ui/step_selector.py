"""Step selector grid component."""

import streamlit as st

from ui.config.constants import (
    OPTIMAL_COLS_THRESHOLD,
    SELECTION_COLORS,
    STATE_SELECTED_NOTES,
    STEP_SELECTOR_WIDE_COLS,
    UNSELECTED_COLOR,
)


def render_step_selector(edo: int, selected_notes: list[int], num_notes: int) -> None:
    """Render EDO step selection grid.

    Args:
        edo: Number of equal divisions of the octave
        selected_notes: Currently selected note indices
        num_notes: Maximum number of notes to select
    """
    st.header("EDO Steps")
    st.caption(f"Step range: 0-{edo - 1} ({edo}-EDO)")

    # 最適な列数を計算(視認性と操作性のバランス)
    optimal_cols = (
        STEP_SELECTOR_WIDE_COLS
        if edo > OPTIMAL_COLS_THRESHOLD
        else min(OPTIMAL_COLS_THRESHOLD, edo)
    )
    num_rows = (edo + optimal_cols - 1) // optimal_cols

    # グリッド生成: 各行を処理
    for row_idx in range(num_rows):
        cols = st.columns(optimal_cols)

        # 各列のインデックスを計算して処理
        for idx in range(row_idx * optimal_cols, min((row_idx + 1) * optimal_cols, edo)):
            col_idx = idx % optimal_cols
            is_selected = idx in selected_notes

            with cols[col_idx]:
                # ボタンクリック処理
                if st.button(
                    str(idx),
                    key=f"idx_{idx}",
                    type="primary" if is_selected else "secondary",
                    use_container_width=True,
                ):
                    # トグル処理
                    if is_selected:
                        st.session_state[STATE_SELECTED_NOTES].remove(idx)
                    else:
                        # 上限到達時は最後の音を置き換え
                        if len(st.session_state[STATE_SELECTED_NOTES]) >= num_notes:
                            st.session_state[STATE_SELECTED_NOTES].pop(-1)
                        st.session_state[STATE_SELECTED_NOTES].append(idx)
                    st.rerun()


def render_selection_status(edo: int, selected_notes: list[int]) -> None:
    """Render selected notes status with visual indicator.

    Args:
        edo: Number of equal divisions of the octave
        selected_notes: Currently selected note indices
    """
    if selected_notes:
        # 昇順にソートして表示
        sorted_notes = sorted(selected_notes)
        st.caption(f"Selected steps S = {{{', '.join(map(str, sorted_notes))}}}")

        # 視覚的なインジケーター (全インデックスを表示)
        indicator_cols = st.columns(edo)
        for i in range(edo):
            with indicator_cols[i]:
                if i in selected_notes:
                    order = sorted_notes.index(i)
                    # カラーマップで順序を表現
                    st.markdown(f"{SELECTION_COLORS[order % len(SELECTION_COLORS)]}")
                else:
                    st.markdown(UNSELECTED_COLOR)

    else:
        st.info("↑ Please select steps")
