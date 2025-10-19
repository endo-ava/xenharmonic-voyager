"""ディソナンス曲線グラフ生成モジュールのテスト"""

from dataclasses import FrozenInstanceError

import numpy as np
import pytest
from plotly.graph_objects import Figure

from src.application.use_cases import CalculateConsonanceUseCase
from src.visualization.dissonance_curve import (
    DissonanceCurveViewModel,
    create_dissonance_curve_graph,
    generate_dissonance_curve_data,
    prepare_dissonance_curve_view_model,
)


class TestGenerateDissonanceCurveData:
    """generate_dissonance_curve_data関数のテスト"""

    def test_returns_correct_array_sizes(self):
        """正しいサイズの配列を返すことを確認"""
        x_vals, g_vals = generate_dissonance_curve_data(num_points=100)

        assert len(x_vals) == 100
        assert len(g_vals) == 100

    def test_x_values_range(self):
        """X値の範囲が正しいことを確認"""
        x_vals, _ = generate_dissonance_curve_data(x_min=0.0, x_max=2.0, num_points=101)

        assert x_vals[0] == pytest.approx(0.0)
        assert x_vals[-1] == pytest.approx(2.0)

    def test_dissonance_at_zero_is_zero(self):
        """x=0でg(x)=0となることを確認"""
        x_vals, g_vals = generate_dissonance_curve_data(num_points=500)

        # x=0に最も近いインデックス
        zero_idx = np.argmin(np.abs(x_vals))
        assert g_vals[zero_idx] == pytest.approx(0.0, abs=1e-10)

    def test_peak_near_quarter(self):
        """ピークがx≈0.24付近にあることを確認"""
        x_vals, g_vals = generate_dissonance_curve_data(x_min=0.0, x_max=1.0, num_points=1000)

        # ピーク位置を見つける
        peak_idx = np.argmax(g_vals)
        peak_x = x_vals[peak_idx]

        # ピーク位置が0.2〜0.3の範囲にあることを確認
        assert 0.2 <= peak_x <= 0.3

    def test_dissonance_decreases_after_peak(self):
        """ピーク後にディソナンス値が減少することを確認"""
        _, g_vals = generate_dissonance_curve_data(x_min=0.0, x_max=2.0, num_points=500)

        peak_idx = np.argmax(g_vals)

        # ピーク後の値がピーク値より小さいことを確認
        if peak_idx < len(g_vals) - 50:
            assert g_vals[peak_idx + 50] < g_vals[peak_idx]


class TestPrepareDissonanceCurveViewModel:
    """prepare_dissonance_curve_view_model関数のテスト"""

    def test_returns_none_for_empty_pair_details(self):
        """空のペア詳細に対してNoneを返すことを確認"""
        vm = prepare_dissonance_curve_view_model(None)
        assert vm is None

        vm = prepare_dissonance_curve_view_model([])
        assert vm is None

    def test_creates_valid_view_model(self):
        """有効なViewModelを作成することを確認"""
        use_case = CalculateConsonanceUseCase()
        result = use_case.execute(
            edo=12, notes=[0, 4, 7], num_harmonics=10, include_pair_details=True
        )

        vm = prepare_dissonance_curve_view_model(result.pair_details)

        assert vm is not None
        assert isinstance(vm, DissonanceCurveViewModel)
        assert isinstance(vm.fig, Figure)
        assert vm.total_pairs == 435  # C(30, 2)
        assert vm.displayed_pairs > 0
        assert vm.displayed_pairs <= vm.total_pairs

    def test_filtering_reduces_displayed_pairs(self):
        """フィルタリングにより表示ペア数が減少することを確認"""
        use_case = CalculateConsonanceUseCase()
        result = use_case.execute(
            edo=12, notes=[0, 4, 7], num_harmonics=10, include_pair_details=True
        )

        # 閾値を高くすると表示ペア数が減る
        vm_low_threshold = prepare_dissonance_curve_view_model(
            result.pair_details, filter_threshold=0.001
        )
        vm_high_threshold = prepare_dissonance_curve_view_model(
            result.pair_details, filter_threshold=0.01
        )

        assert vm_low_threshold is not None
        assert vm_high_threshold is not None
        assert vm_high_threshold.displayed_pairs < vm_low_threshold.displayed_pairs

    def test_statistics_are_consistent(self):
        """統計情報の一貫性を確認"""
        use_case = CalculateConsonanceUseCase()
        result = use_case.execute(
            edo=12, notes=[0, 4, 7], num_harmonics=10, include_pair_details=True
        )

        vm = prepare_dissonance_curve_view_model(result.pair_details)

        assert vm is not None
        # フィルタリング前の統計
        assert vm.total_pairs == vm.self_interference_all + vm.mutual_interference_all
        # フィルタリング後の統計
        assert vm.displayed_pairs == vm.self_interference_filtered + vm.mutual_interference_filtered
        # フィルタリング後はフィルタリング前以下
        assert vm.self_interference_filtered <= vm.self_interference_all
        assert vm.mutual_interference_filtered <= vm.mutual_interference_all

    def test_view_model_is_immutable(self):
        """ViewModelが不変であることを確認"""
        use_case = CalculateConsonanceUseCase()
        result = use_case.execute(
            edo=12, notes=[0, 4, 7], num_harmonics=10, include_pair_details=True
        )

        vm = prepare_dissonance_curve_view_model(result.pair_details)

        assert vm is not None
        with pytest.raises(FrozenInstanceError):  # dataclass(frozen=True)によるエラー
            vm.total_pairs = 999  # type: ignore


class TestIntegration:
    """統合テスト"""

    def test_full_workflow_major_triad(self):
        """長三和音の完全なワークフローをテスト"""
        # 12-EDOの長三和音 [0, 4, 7]
        use_case = CalculateConsonanceUseCase()
        result = use_case.execute(
            edo=12, notes=[0, 4, 7], num_harmonics=10, include_pair_details=True
        )

        assert result.pair_details is not None
        assert len(result.pair_details) == 435  # C(30, 2)

        fig = create_dissonance_curve_graph(result.pair_details)

        assert isinstance(fig, Figure)
        assert len(fig.data) >= 1

    def test_full_workflow_minor_second(self):
        """短2度の完全なワークフローをテスト"""
        # 12-EDOの短2度 [0, 1]
        use_case = CalculateConsonanceUseCase()
        result = use_case.execute(edo=12, notes=[0, 1], num_harmonics=10, include_pair_details=True)

        assert result.pair_details is not None
        assert len(result.pair_details) == 190  # C(20, 2)

        fig = create_dissonance_curve_graph(result.pair_details)

        assert isinstance(fig, Figure)

    def test_different_edo_systems(self):
        """異なるEDOシステムでもテスト"""
        use_case = CalculateConsonanceUseCase()
        for edo in [12, 19, 31]:
            result = use_case.execute(
                edo=edo, notes=[0, edo // 2], num_harmonics=5, include_pair_details=True
            )

            assert result.pair_details is not None
            assert len(result.pair_details) > 0

            fig = create_dissonance_curve_graph(result.pair_details)
            assert isinstance(fig, Figure)
