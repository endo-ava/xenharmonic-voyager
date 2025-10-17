"""src/visualization/history_presenter.py の純粋関数のテスト"""

from unittest.mock import MagicMock

from config.constants import MAX_HISTORY_SIZE, STATE_OBSERVATION_HISTORY, STATE_PINNED_OBSERVATIONS
from src.visualization.history_presenter import (
    HistoryViewModel,
    ObservationItemViewModel,
    get_all_observations,
    pin_observation,
    prepare_history_view_model,
    record_observation,
    unpin_observation,
)
from ui.models import Observation


class TestRecordObservation:
    """record_observation関数のテスト"""

    def test_add_to_empty_history(self, monkeypatch):
        """空の履歴に観測を追加"""
        # モック設定
        mock_st = MagicMock()
        mock_st.session_state = {STATE_OBSERVATION_HISTORY: []}
        monkeypatch.setattr("src.visualization.history_presenter.st", mock_st)

        # 実行
        record_observation(edo=12, notes=[0, 4, 7], roughness=0.5)

        # 検証
        history = mock_st.session_state[STATE_OBSERVATION_HISTORY]
        assert len(history) == 1
        assert history[0] == Observation(edo=12, notes=(0, 4, 7), roughness=0.5)

    def test_add_different_observation(self, monkeypatch):
        """異なる観測を追加"""
        # モック設定
        mock_st = MagicMock()
        mock_st.session_state = {
            STATE_OBSERVATION_HISTORY: [Observation(edo=12, notes=(0, 4, 7), roughness=0.5)]
        }
        monkeypatch.setattr("src.visualization.history_presenter.st", mock_st)

        # 実行
        record_observation(edo=19, notes=[0, 6, 11], roughness=0.3)

        # 検証
        history = mock_st.session_state[STATE_OBSERVATION_HISTORY]
        assert len(history) == 2
        assert history[1] == Observation(edo=19, notes=(0, 6, 11), roughness=0.3)

    def test_skip_duplicate_observation(self, monkeypatch):
        """直前と同じ観測は追加されない"""
        # モック設定
        mock_st = MagicMock()
        existing_obs = Observation(edo=12, notes=(0, 4, 7), roughness=0.5)
        mock_st.session_state = {STATE_OBSERVATION_HISTORY: [existing_obs]}
        monkeypatch.setattr("src.visualization.history_presenter.st", mock_st)

        # 実行(同じ値を追加しようとする)
        record_observation(edo=12, notes=[0, 4, 7], roughness=0.5)

        # 検証: 追加されていない
        history = mock_st.session_state[STATE_OBSERVATION_HISTORY]
        assert len(history) == 1
        assert history[0] == existing_obs

    def test_add_after_different_last_observation(self, monkeypatch):
        """直前と異なる観測は追加される(重複チェックは最後のみ)"""
        # モック設定
        mock_st = MagicMock()
        mock_st.session_state = {
            STATE_OBSERVATION_HISTORY: [
                Observation(edo=12, notes=(0, 4, 7), roughness=0.5),
                Observation(edo=19, notes=(0, 6, 11), roughness=0.3),
            ]
        }
        monkeypatch.setattr("src.visualization.history_presenter.st", mock_st)

        # 実行: 履歴の最初と同じだが、直前とは異なる観測
        record_observation(edo=12, notes=[0, 4, 7], roughness=0.5)

        # 検証: 追加される
        history = mock_st.session_state[STATE_OBSERVATION_HISTORY]
        assert len(history) == 3
        assert history[2] == Observation(edo=12, notes=(0, 4, 7), roughness=0.5)

    def test_limit_history_size_to_max(self, monkeypatch):
        """履歴が最大件数を超えたら古いものを削除"""
        # モック設定: MAX_HISTORY_SIZE件の履歴を作成
        mock_st = MagicMock()
        mock_st.session_state = {
            STATE_OBSERVATION_HISTORY: [
                Observation(edo=i, notes=(0,), roughness=float(i)) for i in range(MAX_HISTORY_SIZE)
            ]
        }
        monkeypatch.setattr("src.visualization.history_presenter.st", mock_st)

        # 実行: 新しい観測を追加
        record_observation(edo=999, notes=[0, 1], roughness=99.9)

        # 検証
        history = mock_st.session_state[STATE_OBSERVATION_HISTORY]
        assert len(history) == MAX_HISTORY_SIZE
        # 最も古い履歴(edo=0)が削除されている
        assert history[0].edo == 1
        # 最新の履歴が追加されている
        assert history[-1] == Observation(edo=999, notes=(0, 1), roughness=99.9)

    def test_notes_converted_to_tuple(self, monkeypatch):
        """notes引数がlistでもtupleに変換される"""
        # モック設定
        mock_st = MagicMock()
        mock_st.session_state = {STATE_OBSERVATION_HISTORY: []}
        monkeypatch.setattr("src.visualization.history_presenter.st", mock_st)

        # 実行: listを渡す
        record_observation(edo=12, notes=[0, 4, 7], roughness=0.5)

        # 検証: tupleに変換されている
        history = mock_st.session_state[STATE_OBSERVATION_HISTORY]
        assert isinstance(history[0].notes, tuple)
        assert history[0].notes == (0, 4, 7)

    def test_empty_notes_list(self, monkeypatch):
        """空のnotesリストでも正常に動作"""
        # モック設定
        mock_st = MagicMock()
        mock_st.session_state = {STATE_OBSERVATION_HISTORY: []}
        monkeypatch.setattr("src.visualization.history_presenter.st", mock_st)

        # 実行
        record_observation(edo=12, notes=[], roughness=0.0)

        # 検証
        history = mock_st.session_state[STATE_OBSERVATION_HISTORY]
        assert len(history) == 1
        assert history[0].notes == ()


class TestGetAllObservations:
    """get_all_observations関数のテスト"""

    def test_empty_history_and_pinned(self, monkeypatch):
        """履歴もピン留めも空の場合"""
        # モック設定
        mock_st = MagicMock()
        mock_st.session_state = {
            STATE_OBSERVATION_HISTORY: [],
            STATE_PINNED_OBSERVATIONS: [],
        }
        monkeypatch.setattr("src.visualization.history_presenter.st", mock_st)

        # 実行
        result = get_all_observations()

        # 検証
        assert result == []

    def test_only_pinned_observations(self, monkeypatch):
        """ピン留めのみ存在する場合"""
        # モック設定
        mock_st = MagicMock()
        pinned_obs = Observation(edo=12, notes=(0, 4, 7), roughness=0.5)
        mock_st.session_state = {
            STATE_OBSERVATION_HISTORY: [],
            STATE_PINNED_OBSERVATIONS: [pinned_obs],
        }
        monkeypatch.setattr("src.visualization.history_presenter.st", mock_st)

        # 実行
        result = get_all_observations()

        # 検証
        assert len(result) == 1
        assert result[0]["obs"] == pinned_obs
        assert result[0]["is_pinned"] is True
        assert result[0]["pin_idx"] == 0

    def test_only_history_observations(self, monkeypatch):
        """履歴のみ存在する場合"""
        # モック設定
        mock_st = MagicMock()
        history_obs = Observation(edo=19, notes=(0, 6, 11), roughness=0.3)
        mock_st.session_state = {
            STATE_OBSERVATION_HISTORY: [history_obs],
            STATE_PINNED_OBSERVATIONS: [],
        }
        monkeypatch.setattr("src.visualization.history_presenter.st", mock_st)

        # 実行
        result = get_all_observations()

        # 検証
        assert len(result) == 1
        assert result[0]["obs"] == history_obs
        assert result[0]["is_pinned"] is False
        assert result[0]["history_idx"] == 0

    def test_pinned_comes_before_unpinned(self, monkeypatch):
        """ピン留めが履歴より前に来る"""
        # モック設定
        mock_st = MagicMock()
        pinned_obs = Observation(edo=12, notes=(0, 4, 7), roughness=0.5)
        history_obs = Observation(edo=19, notes=(0, 6, 11), roughness=0.3)
        mock_st.session_state = {
            STATE_OBSERVATION_HISTORY: [history_obs],
            STATE_PINNED_OBSERVATIONS: [pinned_obs],
        }
        monkeypatch.setattr("src.visualization.history_presenter.st", mock_st)

        # 実行
        result = get_all_observations()

        # 検証
        assert len(result) == 2
        assert result[0]["is_pinned"] is True
        assert result[1]["is_pinned"] is False

    def test_pinned_excluded_from_unpinned(self, monkeypatch):
        """ピン留めされた観測は履歴側から除外される"""
        # モック設定
        mock_st = MagicMock()
        shared_obs = Observation(edo=12, notes=(0, 4, 7), roughness=0.5)
        history_only_obs = Observation(edo=19, notes=(0, 6, 11), roughness=0.3)
        mock_st.session_state = {
            STATE_OBSERVATION_HISTORY: [shared_obs, history_only_obs],
            STATE_PINNED_OBSERVATIONS: [shared_obs],
        }
        monkeypatch.setattr("src.visualization.history_presenter.st", mock_st)

        # 実行
        result = get_all_observations()

        # 検証: 重複なく2件のみ
        assert len(result) == 2
        assert result[0]["obs"] == shared_obs
        assert result[0]["is_pinned"] is True
        assert result[1]["obs"] == history_only_obs
        assert result[1]["is_pinned"] is False

    def test_history_reversed_order(self, monkeypatch):
        """履歴は逆順(新しい順)で返される"""
        # モック設定
        mock_st = MagicMock()
        obs1 = Observation(edo=12, notes=(0,), roughness=0.1)
        obs2 = Observation(edo=19, notes=(1,), roughness=0.2)
        obs3 = Observation(edo=31, notes=(2,), roughness=0.3)
        mock_st.session_state = {
            STATE_OBSERVATION_HISTORY: [obs1, obs2, obs3],
            STATE_PINNED_OBSERVATIONS: [],
        }
        monkeypatch.setattr("src.visualization.history_presenter.st", mock_st)

        # 実行
        result = get_all_observations()

        # 検証: 逆順になっている
        assert len(result) == 3
        assert result[0]["obs"] == obs3  # 最新
        assert result[1]["obs"] == obs2
        assert result[2]["obs"] == obs1  # 最古

    def test_multiple_pinned_with_indices(self, monkeypatch):
        """複数のピン留めがインデックス付きで返される"""
        # モック設定
        mock_st = MagicMock()
        pinned1 = Observation(edo=12, notes=(0,), roughness=0.1)
        pinned2 = Observation(edo=19, notes=(1,), roughness=0.2)
        mock_st.session_state = {
            STATE_OBSERVATION_HISTORY: [],
            STATE_PINNED_OBSERVATIONS: [pinned1, pinned2],
        }
        monkeypatch.setattr("src.visualization.history_presenter.st", mock_st)

        # 実行
        result = get_all_observations()

        # 検証
        assert len(result) == 2
        assert result[0]["pin_idx"] == 0
        assert result[1]["pin_idx"] == 1

    def test_history_indices_reflect_reversed_position(self, monkeypatch):
        """履歴のインデックスは逆順後の位置を反映"""
        # モック設定
        mock_st = MagicMock()
        obs1 = Observation(edo=12, notes=(0,), roughness=0.1)
        obs2 = Observation(edo=19, notes=(1,), roughness=0.2)
        mock_st.session_state = {
            STATE_OBSERVATION_HISTORY: [obs1, obs2],
            STATE_PINNED_OBSERVATIONS: [],
        }
        monkeypatch.setattr("src.visualization.history_presenter.st", mock_st)

        # 実行
        result = get_all_observations()

        # 検証: 逆順なので、obs2がhistory_idx=0、obs1がhistory_idx=1
        assert result[0]["history_idx"] == 0  # obs2(最新)
        assert result[1]["history_idx"] == 1  # obs1(古い)


class TestPrepareHistoryViewModel:
    """prepare_history_view_model関数のテスト"""

    def test_creates_valid_view_model(self, monkeypatch):
        """有効なViewModelを作成する"""
        # モック設定
        mock_st = MagicMock()
        obs1 = Observation(edo=12, notes=(0, 4, 7), roughness=0.5)
        obs2 = Observation(edo=19, notes=(0, 6, 11), roughness=0.3)
        mock_st.session_state = {
            STATE_OBSERVATION_HISTORY: [obs1, obs2],
            STATE_PINNED_OBSERVATIONS: [],
        }
        monkeypatch.setattr("src.visualization.history_presenter.st", mock_st)

        # 実行
        vm = prepare_history_view_model()

        # 検証
        assert isinstance(vm, HistoryViewModel)
        assert len(vm.items) == 2
        assert all(isinstance(item, ObservationItemViewModel) for item in vm.items)

    def test_empty_history_creates_empty_view_model(self, monkeypatch):
        """空の履歴で空のViewModelを作成"""
        # モック設定
        mock_st = MagicMock()
        mock_st.session_state = {
            STATE_OBSERVATION_HISTORY: [],
            STATE_PINNED_OBSERVATIONS: [],
        }
        monkeypatch.setattr("src.visualization.history_presenter.st", mock_st)

        # 実行
        vm = prepare_history_view_model()

        # 検証
        assert isinstance(vm, HistoryViewModel)
        assert len(vm.items) == 0

    def test_view_model_items_have_correct_structure(self, monkeypatch):
        """ViewModelのアイテムが正しい構造を持つ"""
        # モック設定
        mock_st = MagicMock()
        obs = Observation(edo=12, notes=(0, 4, 7), roughness=0.5)
        mock_st.session_state = {
            STATE_OBSERVATION_HISTORY: [obs],
            STATE_PINNED_OBSERVATIONS: [],
        }
        monkeypatch.setattr("src.visualization.history_presenter.st", mock_st)

        # 実行
        vm = prepare_history_view_model()

        # 検証
        item = vm.items[0]
        assert item.obs == obs
        assert item.is_pinned is False
        assert isinstance(item.index, int)


class TestPinObservation:
    """pin_observation関数のテスト"""

    def test_pin_to_empty_list(self, monkeypatch):
        """空のピン留めリストに観測を追加"""
        # モック設定
        mock_st = MagicMock()
        mock_st.session_state = {STATE_PINNED_OBSERVATIONS: []}
        monkeypatch.setattr("src.visualization.history_presenter.st", mock_st)

        # 実行
        obs = Observation(edo=12, notes=(0, 4, 7), roughness=0.5)
        pin_observation(obs)

        # 検証
        pinned = mock_st.session_state[STATE_PINNED_OBSERVATIONS]
        assert len(pinned) == 1
        assert pinned[0] == obs

    def test_pin_multiple_observations(self, monkeypatch):
        """複数の観測をピン留め"""
        # モック設定
        mock_st = MagicMock()
        obs1 = Observation(edo=12, notes=(0, 4, 7), roughness=0.5)
        mock_st.session_state = {STATE_PINNED_OBSERVATIONS: [obs1]}
        monkeypatch.setattr("src.visualization.history_presenter.st", mock_st)

        # 実行
        obs2 = Observation(edo=19, notes=(0, 6, 11), roughness=0.3)
        pin_observation(obs2)

        # 検証
        pinned = mock_st.session_state[STATE_PINNED_OBSERVATIONS]
        assert len(pinned) == 2
        assert pinned[0] == obs1
        assert pinned[1] == obs2

    def test_pin_duplicate_observation(self, monkeypatch):
        """同じ観測を複数回ピン留めできる(重複チェックなし)"""
        # モック設定
        mock_st = MagicMock()
        obs = Observation(edo=12, notes=(0, 4, 7), roughness=0.5)
        mock_st.session_state = {STATE_PINNED_OBSERVATIONS: [obs]}
        monkeypatch.setattr("src.visualization.history_presenter.st", mock_st)

        # 実行: 同じ観測をピン留め
        pin_observation(obs)

        # 検証: 重複してピン留めされる
        pinned = mock_st.session_state[STATE_PINNED_OBSERVATIONS]
        assert len(pinned) == 2
        assert pinned[0] == obs
        assert pinned[1] == obs


class TestUnpinObservation:
    """unpin_observation関数のテスト"""

    def test_unpin_single_observation(self, monkeypatch):
        """単一のピン留めを解除"""
        # モック設定
        mock_st = MagicMock()
        obs = Observation(edo=12, notes=(0, 4, 7), roughness=0.5)
        mock_st.session_state = {STATE_PINNED_OBSERVATIONS: [obs]}
        monkeypatch.setattr("src.visualization.history_presenter.st", mock_st)

        # 実行
        unpin_observation(0)

        # 検証
        pinned = mock_st.session_state[STATE_PINNED_OBSERVATIONS]
        assert len(pinned) == 0

    def test_unpin_from_multiple_observations(self, monkeypatch):
        """複数のピン留めから1つを解除"""
        # モック設定
        mock_st = MagicMock()
        obs1 = Observation(edo=12, notes=(0, 4, 7), roughness=0.5)
        obs2 = Observation(edo=19, notes=(0, 6, 11), roughness=0.3)
        obs3 = Observation(edo=31, notes=(0, 10, 18), roughness=0.2)
        mock_st.session_state = {STATE_PINNED_OBSERVATIONS: [obs1, obs2, obs3]}
        monkeypatch.setattr("src.visualization.history_presenter.st", mock_st)

        # 実行: 中央の要素を解除
        unpin_observation(1)

        # 検証
        pinned = mock_st.session_state[STATE_PINNED_OBSERVATIONS]
        assert len(pinned) == 2
        assert pinned[0] == obs1
        assert pinned[1] == obs3

    def test_unpin_first_observation(self, monkeypatch):
        """最初のピン留めを解除"""
        # モック設定
        mock_st = MagicMock()
        obs1 = Observation(edo=12, notes=(0,), roughness=0.1)
        obs2 = Observation(edo=19, notes=(1,), roughness=0.2)
        mock_st.session_state = {STATE_PINNED_OBSERVATIONS: [obs1, obs2]}
        monkeypatch.setattr("src.visualization.history_presenter.st", mock_st)

        # 実行
        unpin_observation(0)

        # 検証
        pinned = mock_st.session_state[STATE_PINNED_OBSERVATIONS]
        assert len(pinned) == 1
        assert pinned[0] == obs2

    def test_unpin_last_observation(self, monkeypatch):
        """最後のピン留めを解除"""
        # モック設定
        mock_st = MagicMock()
        obs1 = Observation(edo=12, notes=(0,), roughness=0.1)
        obs2 = Observation(edo=19, notes=(1,), roughness=0.2)
        mock_st.session_state = {STATE_PINNED_OBSERVATIONS: [obs1, obs2]}
        monkeypatch.setattr("src.visualization.history_presenter.st", mock_st)

        # 実行
        unpin_observation(1)

        # 検証
        pinned = mock_st.session_state[STATE_PINNED_OBSERVATIONS]
        assert len(pinned) == 1
        assert pinned[0] == obs1
