"""ディソナンス曲線グラフ生成モジュールのテスト"""

import numpy as np
import pytest
from plotly.graph_objects import Figure

from src.calculator import calculate_consonance_with_details
from src.visualization.dissonance_curve import (
    create_dissonance_curve_graph,
    generate_dissonance_curve_data,
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


class TestIntegration:
    """統合テスト"""

    def test_full_workflow_major_triad(self):
        """長三和音の完全なワークフローをテスト"""
        # 12-EDOの長三和音 [0, 4, 7]
        result = calculate_consonance_with_details(edo=12, notes=[0, 4, 7], num_harmonics=10)

        assert result.pair_details is not None
        assert len(result.pair_details) == 435  # C(30, 2)

        fig = create_dissonance_curve_graph(result.pair_details)

        assert isinstance(fig, Figure)
        assert len(fig.data) >= 1

    def test_full_workflow_minor_second(self):
        """短2度の完全なワークフローをテスト"""
        # 12-EDOの短2度 [0, 1]
        result = calculate_consonance_with_details(edo=12, notes=[0, 1], num_harmonics=10)

        assert result.pair_details is not None
        assert len(result.pair_details) == 190  # C(20, 2)

        fig = create_dissonance_curve_graph(result.pair_details)

        assert isinstance(fig, Figure)

    def test_different_edo_systems(self):
        """異なるEDOシステムでもテスト"""
        for edo in [12, 19, 31]:
            result = calculate_consonance_with_details(
                edo=edo, notes=[0, edo // 2], num_harmonics=5
            )

            assert result.pair_details is not None
            assert len(result.pair_details) > 0

            fig = create_dissonance_curve_graph(result.pair_details)
            assert isinstance(fig, Figure)
