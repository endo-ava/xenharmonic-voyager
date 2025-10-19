"""UI layer session state management

このモジュールは、Streamlitセッション状態の管理を担当します。
Presenter層の純粋関数と、UI層のセッション状態を橋渡しします。
"""

import streamlit as st

from src.visualization.models import Observation
from ui.config.constants import (
    MAX_HISTORY_SIZE,
    STATE_OBSERVATION_HISTORY,
    STATE_PINNED_OBSERVATIONS,
)


def record_observation_to_session(edo: int, notes: list[int], roughness: float) -> None:
    """観測結果をセッション状態の履歴に記録します。

    直前と同じ観測の場合はスキップし、最大件数を超えた場合は古いものを削除します。

    Args:
        edo: EDO値
        notes: 選択された音符インデックスのリスト
        roughness: 計算されたラフネス値

    Examples:
        >>> record_observation_to_session(edo=12, notes=[0, 4, 7], roughness=0.5)
    """
    current_observation = Observation(edo=edo, notes=tuple(notes), roughness=roughness)

    history = st.session_state[STATE_OBSERVATION_HISTORY]
    # 履歴の最後と同じでなければ追加
    if not history or history[-1] != current_observation:
        history.append(current_observation)
        # 最大件数に制限
        if len(history) > MAX_HISTORY_SIZE:
            history.pop(0)


def get_observations_from_session() -> list[Observation]:
    """セッション状態から観測履歴を取得します。

    Returns:
        list[Observation]: 観測履歴のリスト
    """
    return st.session_state[STATE_OBSERVATION_HISTORY]


def get_pinned_observations_from_session() -> list[Observation]:
    """セッション状態からピン留めされた観測を取得します。

    Returns:
        list[Observation]: ピン留めされた観測のリスト
    """
    return st.session_state[STATE_PINNED_OBSERVATIONS]


def pin_observation_in_session(obs: Observation) -> None:
    """観測をセッション状態にピン留めします。

    Args:
        obs: ピン留めする観測

    Examples:
        >>> obs = Observation(edo=12, notes=(0, 4, 7), roughness=0.5)
        >>> pin_observation_in_session(obs)
    """
    st.session_state[STATE_PINNED_OBSERVATIONS].append(obs)


def unpin_observation_in_session(pin_idx: int) -> None:
    """セッション状態から観測のピン留めを解除します。

    Args:
        pin_idx: ピン留めリスト内のインデックス

    Examples:
        >>> unpin_observation_in_session(0)  # 最初のピン留めを解除
    """
    st.session_state[STATE_PINNED_OBSERVATIONS].pop(pin_idx)
