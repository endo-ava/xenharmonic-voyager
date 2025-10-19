"""History view用のPresenter層

このモジュールは、観測履歴のビジネスロジックとUI表示データの準備を担当します。
純粋関数として実装されており、セッション状態に依存しません。
"""

from typing import TypedDict

from src.visualization.models import HistoryViewModel, Observation, ObservationItemViewModel


class ObservationItem(TypedDict, total=False):
    """get_all_observations()の戻り値型 (内部用ヘルパー型)

    Attributes:
        obs: 観測データ
        is_pinned: ピン留めされているか
        pin_idx: ピン留めリスト内のインデックス (ピン留めの場合のみ)
        history_idx: 履歴リスト内のインデックス (履歴の場合のみ)
    """

    obs: Observation
    is_pinned: bool
    pin_idx: int
    history_idx: int


def get_all_observations(
    history: list[Observation],
    pinned: list[Observation],
) -> list[ObservationItem]:
    """すべての観測 (ピン留め + 履歴) を取得します。

    ピン留めされた観測を先頭に、その後履歴の観測を新しい順で返します。
    ピン留めされた観測は履歴側から除外されます。

    Args:
        history: 観測履歴のリスト
        pinned: ピン留めされた観測のリスト

    Returns:
        list[ObservationItem]: 観測アイテムのリスト。各アイテムは以下のキーを持つ:
            - obs: Observation オブジェクト
            - is_pinned: bool (ピン留めフラグ)
            - pin_idx: int (ピン留めの場合のインデックス、履歴の場合は存在しない)
            - history_idx: int (履歴の場合のインデックス、ピン留めの場合は存在しない)

    Examples:
        >>> history = [Observation(edo=12, notes=(0,), roughness=0.1)]
        >>> pinned = [Observation(edo=19, notes=(1,), roughness=0.2)]
        >>> items = get_all_observations(history, pinned)
        >>> items[0]["is_pinned"]
        True
    """
    pinned_items: list[ObservationItem] = [
        {"obs": obs, "is_pinned": True, "pin_idx": idx} for idx, obs in enumerate(pinned)
    ]
    # Use set for O(1) lookup performance
    pinned_set = set(pinned)
    unpinned_items: list[ObservationItem] = [
        {"obs": obs, "is_pinned": False, "history_idx": idx}
        for idx, obs in enumerate(reversed(history))
        if obs not in pinned_set
    ]
    return pinned_items + unpinned_items


def prepare_history_view_model(
    history: list[Observation],
    pinned: list[Observation],
) -> HistoryViewModel:
    """HistoryViewModelを準備します。

    観測履歴とピン留めリストから、表示用のViewModelを構築します。

    Args:
        history: 観測履歴のリスト
        pinned: ピン留めされた観測のリスト

    Returns:
        HistoryViewModel: UI表示用の準備されたデータモデル

    Examples:
        >>> history = [Observation(edo=12, notes=(0, 4, 7), roughness=0.5)]
        >>> pinned = []
        >>> vm = prepare_history_view_model(history, pinned)
        >>> len(vm.items)
        1
    """
    all_obs = get_all_observations(history, pinned)
    items = [
        ObservationItemViewModel(
            obs=item["obs"],
            is_pinned=item["is_pinned"],
            index=item["pin_idx"] if item["is_pinned"] else item["history_idx"],
        )
        for item in all_obs
    ]
    return HistoryViewModel(items=items)
