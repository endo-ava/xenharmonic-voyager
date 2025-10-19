"""src/visualization/history_presenter.py の純粋関数のテスト

Streamlit依存を除去した純粋関数として実装されたPresenter関数のテスト。
セッション状態管理のテストは tests/ui/test_session_management.py に移動。
"""

from src.visualization.history_presenter import (
    get_all_observations,
    prepare_history_view_model,
)
from src.visualization.models import HistoryViewModel, Observation, ObservationItemViewModel


class TestGetAllObservations:
    """get_all_observations関数のテスト"""

    def test_empty_history_and_pinned(self):
        """履歴もピン留めも空の場合"""
        result = get_all_observations(history=[], pinned=[])
        assert result == []

    def test_only_pinned_observations(self):
        """ピン留めのみ存在する場合"""
        pinned_obs = Observation(edo=12, notes=(0, 4, 7), roughness=0.5)
        result = get_all_observations(history=[], pinned=[pinned_obs])

        assert len(result) == 1
        assert result[0]["obs"] == pinned_obs
        assert result[0]["is_pinned"] is True
        assert result[0]["pin_idx"] == 0

    def test_only_history_observations(self):
        """履歴のみ存在する場合"""
        history_obs = Observation(edo=19, notes=(0, 6, 11), roughness=0.3)
        result = get_all_observations(history=[history_obs], pinned=[])

        assert len(result) == 1
        assert result[0]["obs"] == history_obs
        assert result[0]["is_pinned"] is False
        assert result[0]["history_idx"] == 0

    def test_pinned_comes_before_unpinned(self):
        """ピン留めが履歴より前に来る"""
        pinned_obs = Observation(edo=12, notes=(0, 4, 7), roughness=0.5)
        history_obs = Observation(edo=19, notes=(0, 6, 11), roughness=0.3)

        result = get_all_observations(history=[history_obs], pinned=[pinned_obs])

        assert len(result) == 2
        assert result[0]["is_pinned"] is True
        assert result[1]["is_pinned"] is False

    def test_pinned_excluded_from_unpinned(self):
        """ピン留めされた観測は履歴側から除外される"""
        shared_obs = Observation(edo=12, notes=(0, 4, 7), roughness=0.5)
        history_only_obs = Observation(edo=19, notes=(0, 6, 11), roughness=0.3)

        result = get_all_observations(history=[shared_obs, history_only_obs], pinned=[shared_obs])

        # 重複なく2件のみ
        assert len(result) == 2
        assert result[0]["obs"] == shared_obs
        assert result[0]["is_pinned"] is True
        assert result[1]["obs"] == history_only_obs
        assert result[1]["is_pinned"] is False

    def test_history_reversed_order(self):
        """履歴は逆順 (新しい順) で返される"""
        obs1 = Observation(edo=12, notes=(0,), roughness=0.1)
        obs2 = Observation(edo=19, notes=(1,), roughness=0.2)
        obs3 = Observation(edo=31, notes=(2,), roughness=0.3)

        result = get_all_observations(history=[obs1, obs2, obs3], pinned=[])

        # 逆順になっている
        assert len(result) == 3
        assert result[0]["obs"] == obs3  # 最新
        assert result[1]["obs"] == obs2
        assert result[2]["obs"] == obs1  # 最古

    def test_multiple_pinned_with_indices(self):
        """複数のピン留めがインデックス付きで返される"""
        pinned1 = Observation(edo=12, notes=(0,), roughness=0.1)
        pinned2 = Observation(edo=19, notes=(1,), roughness=0.2)

        result = get_all_observations(history=[], pinned=[pinned1, pinned2])

        assert len(result) == 2
        assert result[0]["pin_idx"] == 0
        assert result[1]["pin_idx"] == 1

    def test_history_indices_reflect_reversed_position(self):
        """履歴のインデックスは逆順後の位置を反映"""
        obs1 = Observation(edo=12, notes=(0,), roughness=0.1)
        obs2 = Observation(edo=19, notes=(1,), roughness=0.2)

        result = get_all_observations(history=[obs1, obs2], pinned=[])

        # 逆順なので、obs2がhistory_idx=0、obs1がhistory_idx=1
        assert result[0]["history_idx"] == 0  # obs2 (最新)
        assert result[1]["history_idx"] == 1  # obs1 (古い)


class TestPrepareHistoryViewModel:
    """prepare_history_view_model関数のテスト"""

    def test_creates_valid_view_model(self):
        """有効なViewModelを作成する"""
        obs1 = Observation(edo=12, notes=(0, 4, 7), roughness=0.5)
        obs2 = Observation(edo=19, notes=(0, 6, 11), roughness=0.3)

        vm = prepare_history_view_model(history=[obs1, obs2], pinned=[])

        assert isinstance(vm, HistoryViewModel)
        assert len(vm.items) == 2
        assert all(isinstance(item, ObservationItemViewModel) for item in vm.items)

    def test_empty_history_creates_empty_view_model(self):
        """空の履歴で空のViewModelを作成"""
        vm = prepare_history_view_model(history=[], pinned=[])

        assert isinstance(vm, HistoryViewModel)
        assert len(vm.items) == 0

    def test_view_model_items_have_correct_structure(self):
        """ViewModelのアイテムが正しい構造を持つ"""
        obs = Observation(edo=12, notes=(0, 4, 7), roughness=0.5)

        vm = prepare_history_view_model(history=[obs], pinned=[])

        item = vm.items[0]
        assert item.obs == obs
        assert item.is_pinned is False
        assert isinstance(item.index, int)

    def test_pinned_items_have_pin_index(self):
        """ピン留めアイテムがpin_idxを持つ"""
        pinned_obs = Observation(edo=12, notes=(0, 4, 7), roughness=0.5)

        vm = prepare_history_view_model(history=[], pinned=[pinned_obs])

        item = vm.items[0]
        assert item.obs == pinned_obs
        assert item.is_pinned is True
        assert item.index == 0  # pin_idx

    def test_history_items_have_history_index(self):
        """履歴アイテムがhistory_idxを持つ"""
        history_obs = Observation(edo=19, notes=(0, 6, 11), roughness=0.3)

        vm = prepare_history_view_model(history=[history_obs], pinned=[])

        item = vm.items[0]
        assert item.obs == history_obs
        assert item.is_pinned is False
        assert item.index == 0  # history_idx
