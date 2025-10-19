"""src/visualization/analysis_presenter.py の純粋関数のテスト"""

import pytest

from src.visualization.analysis_presenter import (
    AnalysisViewModel,
    calculate_inverted_progress,
    get_roughness_level,
    prepare_analysis_view_model,
)
from ui.config.constants import MAX_ROUGHNESS_FOR_PROGRESS, RoughnessLevel


class TestGetRoughnessLevel:
    """get_roughness_level関数のテスト"""

    def test_very_consonant_lower_bound(self):
        """ラフネスが0.0でVery Consonantを返す"""
        result = get_roughness_level(0.0)
        assert result == "L1 (Very Consonant)"

    def test_very_consonant_just_below_threshold(self):
        """ラフネスが0.5未満でVery Consonantを返す"""
        result = get_roughness_level(0.49)
        assert result == "L1 (Very Consonant)"

    def test_consonant_at_threshold(self):
        """ラフネスが0.5でConsonantを返す"""
        result = get_roughness_level(0.5)
        assert result == "L2 (Consonant)"

    def test_consonant_just_below_threshold(self):
        """ラフネスが1.0未満でConsonantを返す"""
        result = get_roughness_level(0.99)
        assert result == "L2 (Consonant)"

    def test_slightly_consonant_at_threshold(self):
        """ラフネスが1.0でSlightly Consonantを返す"""
        result = get_roughness_level(1.0)
        assert result == "L3 (Slightly Consonant)"

    def test_slightly_consonant_just_below_threshold(self):
        """ラフネスが2.0未満でSlightly Consonantを返す"""
        result = get_roughness_level(1.99)
        assert result == "L3 (Slightly Consonant)"

    def test_slightly_dissonant_at_threshold(self):
        """ラフネスが2.0でSlightly Dissonantを返す"""
        result = get_roughness_level(2.0)
        assert result == "L4 (Slightly Dissonant)"

    def test_slightly_dissonant_just_below_threshold(self):
        """ラフネスが4.0未満でSlightly Dissonantを返す"""
        result = get_roughness_level(3.99)
        assert result == "L4 (Slightly Dissonant)"

    def test_dissonant_at_threshold(self):
        """ラフネスが4.0でDissonantを返す"""
        result = get_roughness_level(4.0)
        assert result == "L5 (Dissonant)"

    def test_dissonant_large_value(self):
        """ラフネスが非常に大きくてもDissonantを返す"""
        result = get_roughness_level(100.0)
        assert result == "L5 (Dissonant)"

    def test_boundary_values_match_constants(self):
        """境界値が定数と一致することを確認"""
        # これはリグレッションテスト: 定数変更時にテストが失敗する
        assert get_roughness_level(RoughnessLevel.VERY_CONSONANT - 0.01) == "L1 (Very Consonant)"
        assert get_roughness_level(RoughnessLevel.VERY_CONSONANT) == "L2 (Consonant)"
        assert get_roughness_level(RoughnessLevel.CONSONANT) == "L3 (Slightly Consonant)"
        assert get_roughness_level(RoughnessLevel.SLIGHTLY_CONSONANT) == "L4 (Slightly Dissonant)"
        assert get_roughness_level(RoughnessLevel.SLIGHTLY_DISSONANT) == "L5 (Dissonant)"


class TestCalculateInvertedProgress:
    """calculate_inverted_progress関数のテスト"""

    def test_zero_roughness_returns_one(self):
        """ラフネスが0.0のとき、進行度は1.0（最大）"""
        result = calculate_inverted_progress(0.0)
        assert result == pytest.approx(1.0)

    def test_max_roughness_returns_zero(self):
        """ラフネスがmax_roughnessのとき、進行度は0.0"""
        result = calculate_inverted_progress(MAX_ROUGHNESS_FOR_PROGRESS)
        assert result == pytest.approx(0.0)

    def test_half_max_roughness_returns_half(self):
        """ラフネスがmax_roughnessの半分のとき、進行度は0.5"""
        result = calculate_inverted_progress(1.0, max_roughness=2.0)
        assert result == pytest.approx(0.5)

    def test_negative_roughness_clamps_to_one(self):
        """負のラフネスは1.0にクランプされる"""
        result = calculate_inverted_progress(-1.0)
        assert result == pytest.approx(1.0)

    def test_exceeding_max_roughness_clamps_to_zero(self):
        """max_roughnessを超えるラフネスは0.0にクランプされる"""
        result = calculate_inverted_progress(10.0, max_roughness=2.0)
        assert result == pytest.approx(0.0)

    def test_custom_max_roughness(self):
        """カスタムmax_roughness引数が正しく機能する"""
        result = calculate_inverted_progress(2.5, max_roughness=5.0)
        assert result == pytest.approx(0.5)

    def test_result_always_in_valid_range(self):
        """戻り値が常に0.0～1.0の範囲内"""
        test_values = [-10.0, -1.0, 0.0, 0.5, 1.0, 1.5, 2.0, 5.0, 100.0]
        for roughness in test_values:
            result = calculate_inverted_progress(roughness)
            assert 0.0 <= result <= 1.0, f"Failed for roughness={roughness}"

    def test_linear_interpolation(self):
        """線形補間が正しく機能する"""
        # max_roughness=10.0で、ラフネスが3.0のとき
        # progress = (10.0 - 3.0) / 10.0 = 0.7
        result = calculate_inverted_progress(3.0, max_roughness=10.0)
        assert result == pytest.approx(0.7)

    def test_default_max_roughness_value(self):
        """デフォルトのmax_roughness値が定数と一致する"""
        # これは実装詳細のリグレッションテスト
        result_explicit = calculate_inverted_progress(1.0, max_roughness=MAX_ROUGHNESS_FOR_PROGRESS)
        result_default = calculate_inverted_progress(1.0)
        assert result_explicit == pytest.approx(result_default)

    def test_inverted_behavior(self):
        """より小さいラフネス値がより大きい進行度を返す（反転動作）"""
        low_roughness_progress = calculate_inverted_progress(0.5)
        high_roughness_progress = calculate_inverted_progress(1.5)
        assert low_roughness_progress > high_roughness_progress


class TestPrepareAnalysisViewModel:
    """prepare_analysis_view_model関数のテスト"""

    def test_creates_valid_view_model(self):
        """有効なViewModelを作成する"""
        vm = prepare_analysis_view_model(0.5)

        assert isinstance(vm, AnalysisViewModel)
        assert vm.roughness == 0.5
        assert vm.roughness_level == "L2 (Consonant)"
        assert 0.0 <= vm.inverted_progress <= 1.0

    def test_very_consonant_case(self):
        """非常に協和的なケース"""
        vm = prepare_analysis_view_model(0.1)

        assert vm.roughness == 0.1
        assert vm.roughness_level == "L1 (Very Consonant)"
        assert vm.inverted_progress > 0.9

    def test_dissonant_case(self):
        """不協和的なケース"""
        vm = prepare_analysis_view_model(5.0)

        assert vm.roughness == 5.0
        assert vm.roughness_level == "L5 (Dissonant)"
        assert vm.inverted_progress == 0.0

    def test_view_model_is_immutable(self):
        """ViewModelが不変であることを確認"""
        vm = prepare_analysis_view_model(1.0)

        # frozenデータクラスなので、属性変更は不可
        with pytest.raises(AttributeError):
            vm.roughness = 2.0  # type: ignore

    def test_multiple_calls_consistent(self):
        """同じ入力で同じ結果を返す（決定的）"""
        vm1 = prepare_analysis_view_model(1.5)
        vm2 = prepare_analysis_view_model(1.5)

        assert vm1.roughness == vm2.roughness
        assert vm1.roughness_level == vm2.roughness_level
        assert vm1.inverted_progress == vm2.inverted_progress
