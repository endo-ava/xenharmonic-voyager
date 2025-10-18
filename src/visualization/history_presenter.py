"""History view用のPresenter層

このモジュールは、観測履歴のビジネスロジックとUI表示データの準備を担当します。
セッション状態の管理とViewModelの準備を分離しています。
"""

from dataclasses import dataclass
from typing import TypedDict

import streamlit as st

from config.constants import (
    MAX_HISTORY_SIZE,
    STATE_OBSERVATION_HISTORY,
    STATE_PINNED_OBSERVATIONS,
)
from ui.models import Observation


class ObservationItem(TypedDict, total=False):
    """get_all_observations()の戻り値型

    Attributes:
        obs: 観測データ
        is_pinned: ピン留めされているか
        pin_idx: ピン留めリスト内のインデックス（ピン留めの場合のみ）
        history_idx: 履歴リスト内のインデックス（履歴の場合のみ）
    """

    obs: Observation
    is_pinned: bool
    pin_idx: int
    history_idx: int


@dataclass(frozen=True)
class ObservationItemViewModel:
    """観測アイテムの表示用データモデル

    Attributes:
        obs: 観測データ
        is_pinned: ピン留めされているか
        index: 項目のインデックス（ピン留めまたは履歴内）
    """

    obs: Observation
    is_pinned: bool
    index: int


@dataclass(frozen=True)
class HistoryViewModel:
    """履歴ビューの表示用データモデル

    Attributes:
        items: 表示する観測アイテムのリスト（ピン留め + 履歴）
    """

    items: list[ObservationItemViewModel]


def record_observation(edo: int, notes: list[int], roughness: float) -> None:
    """観測結果を履歴に記録します。

    セッション状態の観測履歴に新しい観測を追加します。
    直前と同じ観測の場合はスキップし、最大件数を超えた場合は古いものを削除します。

    Args:
        edo: EDO値
        notes: 選択された音符インデックスのリスト
        roughness: 計算されたラフネス値

    Examples:
        >>> record_observation(edo=12, notes=[0, 4, 7], roughness=0.5)
    """
    current_observation = Observation(edo=edo, notes=tuple(notes), roughness=roughness)

    history = st.session_state[STATE_OBSERVATION_HISTORY]
    # 履歴の最後と同じでなければ追加
    if not history or history[-1] != current_observation:
        history.append(current_observation)
        # 最大件数に制限
        if len(history) > MAX_HISTORY_SIZE:
            history.pop(0)


def get_all_observations() -> list[ObservationItem]:
    """すべての観測（ピン留め + 履歴）を取得します。

    ピン留めされた観測を先頭に、その後履歴の観測を新しい順で返します。
    ピン留めされた観測は履歴側から除外されます。

    Returns:
        list[ObservationItem]: 観測アイテムのリスト。各アイテムは以下のキーを持つ:
            - obs: Observation オブジェクト
            - is_pinned: bool (ピン留めフラグ)
            - pin_idx: int (ピン留めの場合のインデックス、履歴の場合は存在しない)
            - history_idx: int (履歴の場合のインデックス、ピン留めの場合は存在しない)

    Examples:
        >>> items = get_all_observations()
        >>> for item in items:
        ...     print(f"Pinned: {item['is_pinned']}, R={item['obs'].roughness}")
    """
    pinned: list[ObservationItem] = [
        {"obs": obs, "is_pinned": True, "pin_idx": idx}
        for idx, obs in enumerate(st.session_state[STATE_PINNED_OBSERVATIONS])
    ]
    # Use set for O(1) lookup performance
    pinned_set = set(st.session_state[STATE_PINNED_OBSERVATIONS])
    unpinned: list[ObservationItem] = [
        {"obs": obs, "is_pinned": False, "history_idx": idx}
        for idx, obs in enumerate(reversed(st.session_state[STATE_OBSERVATION_HISTORY]))
        if obs not in pinned_set
    ]
    return pinned + unpinned


def pin_observation(obs: Observation) -> None:
    """観測をピン留めします。

    Args:
        obs: ピン留めする観測

    Examples:
        >>> obs = Observation(edo=12, notes=(0, 4, 7), roughness=0.5)
        >>> pin_observation(obs)
    """
    st.session_state[STATE_PINNED_OBSERVATIONS].append(obs)


def unpin_observation(pin_idx: int) -> None:
    """観測のピン留めを解除します。

    Args:
        pin_idx: ピン留めリスト内のインデックス

    Examples:
        >>> unpin_observation(0)  # 最初のピン留めを解除
    """
    st.session_state[STATE_PINNED_OBSERVATIONS].pop(pin_idx)


def prepare_history_view_model() -> HistoryViewModel:
    """HistoryViewModelを準備します。

    セッション状態から観測データを取得し、表示用のViewModelに変換します。

    Returns:
        HistoryViewModel: UI表示用の準備されたデータモデル

    Examples:
        >>> vm = prepare_history_view_model()
        >>> for item in vm.items:
        ...     print(f"Pinned: {item.is_pinned}, R={item.obs.roughness}")
    """
    all_obs = get_all_observations()
    items = [
        ObservationItemViewModel(
            obs=item["obs"],
            is_pinned=item["is_pinned"],
            index=item["pin_idx"] if item["is_pinned"] else item["history_idx"],
        )
        for item in all_obs
    ]
    return HistoryViewModel(items=items)
