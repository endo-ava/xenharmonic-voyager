"""協和性計算モジュールのテスト"""

import pytest
from pydantic import ValidationError

from src.calculator import ChordInput, calculate_consonance


class TestChordInput:
    """ChordInput検証のテストケース"""

    def test_valid_chord_input(self):
        """有効な入力が受け入れられること"""
        chord = ChordInput(edo=12, notes=[0, 4, 7])
        assert chord.edo == 12
        assert chord.notes == [0, 4, 7]

    def test_invalid_edo_zero(self):
        """EDOは0より大きいこと"""
        with pytest.raises(ValidationError):
            ChordInput(edo=0, notes=[0, 1, 2])

    def test_invalid_edo_negative(self):
        """EDOは負でないこと"""
        with pytest.raises(ValidationError):
            ChordInput(edo=-1, notes=[0, 1, 2])

    def test_invalid_notes_out_of_range(self):
        """音符はEDO範囲内であること"""
        with pytest.raises(ValidationError):
            ChordInput(edo=12, notes=[0, 4, 12])  # 12は[0-11]の範囲外

    def test_invalid_notes_negative(self):
        """音符は負でないこと"""
        with pytest.raises(ValidationError):
            ChordInput(edo=12, notes=[-1, 0, 4])


class TestCalculateConsonance:
    """協和性計算のテストケース"""

    def test_calculate_consonance_returns_float(self):
        """協和性計算がfloatを返すこと"""
        result = calculate_consonance(edo=12, notes=[0, 4, 7])
        assert isinstance(result, float)

    def test_calculate_consonance_validates_input(self):
        """無効な入力でValidationErrorが発生すること"""
        with pytest.raises(ValidationError):
            calculate_consonance(edo=12, notes=[0, 4, 12])

    def test_calculate_consonance_non_zero_result(self):
        """実際の和音で協和性計算が0以外の値を返すこと"""
        result = calculate_consonance(edo=12, notes=[0, 4, 7])
        assert result > 0.0  # ある程度のラフネスがあるはず

    def test_unison_low_roughness(self):
        """ユニゾンは不協和音程より低いラフネスを持つこと"""
        # ユニゾン(同じ音) - 自己倍音のラフネスのみ
        roughness_unison = calculate_consonance(edo=12, notes=[0])
        roughness_m2 = calculate_consonance(edo=12, notes=[0, 1])

        # ユニゾンは短2度よりも協和的であるべき
        assert roughness_unison < roughness_m2

    def test_minor_second_is_dissonant(self):
        """短2度は高いラフネス(低い協和性)を持つこと"""
        roughness_m2 = calculate_consonance(edo=12, notes=[0, 1])
        roughness_p5 = calculate_consonance(edo=12, notes=[0, 7])

        # 短2度は完全5度よりも不協和であるべき
        assert roughness_m2 > roughness_p5

    def test_major_triad_moderate_roughness(self):
        """長三和音は音程間で中程度のラフネスを持つこと"""
        roughness_triad = calculate_consonance(edo=12, notes=[0, 4, 7])
        roughness_unison = calculate_consonance(edo=12, notes=[0])
        roughness_p5 = calculate_consonance(edo=12, notes=[0, 7])

        # 三和音(3音)はユニゾンや完全5度よりも多くのラフネスを持つべき
        # より多くの倍音ペアを持つため
        assert roughness_unison < roughness_triad
        assert roughness_p5 < roughness_triad

    def test_different_edo_systems(self):
        """異なるEDOシステムで計算が機能すること"""
        # 12-EDO長三和音
        roughness_12edo = calculate_consonance(edo=12, notes=[0, 4, 7])

        # 19-EDO「長」三和音の近似
        roughness_19edo = calculate_consonance(edo=19, notes=[0, 6, 11])

        # 両方とも有効なラフネス値を返すはず
        assert roughness_12edo > 0.0
        assert roughness_19edo > 0.0

        # 結果は異なるはず(異なるチューニングシステム)
        assert roughness_12edo != pytest.approx(roughness_19edo)

    def test_custom_base_frequency(self):
        """カスタム基本周波数は異なる結果を生成すること"""
        roughness_440 = calculate_consonance(edo=12, notes=[0, 4, 7], base_frequency=440.0)
        roughness_220 = calculate_consonance(edo=12, notes=[0, 4, 7], base_frequency=220.0)

        # 異なる基本周波数は異なる絶対ラフネスを生成するはず
        # (臨界帯域幅の周波数依存性のため)
        assert roughness_440 != pytest.approx(roughness_220)

    def test_custom_num_harmonics(self):
        """異なるnum_harmonicsは異なる結果を生成すること"""
        roughness_5harm = calculate_consonance(edo=12, notes=[0, 4, 7], num_harmonics=5)
        roughness_10harm = calculate_consonance(edo=12, notes=[0, 4, 7], num_harmonics=10)

        # より多くの倍音は異なるラフネスを生成するはず
        assert roughness_5harm != pytest.approx(roughness_10harm)

    def test_single_note(self):
        """単一音符の計算"""
        roughness = calculate_consonance(edo=12, notes=[0])

        # 単一の音符は倍音からある程度の自己ラフネスを持つはず
        assert roughness > 0.0

    def test_empty_notes_raises_error(self):
        """空の音符リストでValidationErrorが発生すること"""
        with pytest.raises(ValidationError):
            calculate_consonance(edo=12, notes=[])

    def test_large_chord(self):
        """より大きな和音の計算"""
        # 6音の和音
        roughness = calculate_consonance(edo=12, notes=[0, 2, 4, 5, 7, 9])

        # 有効なラフネスを返すはず
        assert roughness > 0.0

    def test_unison(self):
        """ユニゾン(同音2回)が機能すること"""
        roughness = calculate_consonance(edo=12, notes=[0, 0])

        # クロスハーモニクスからある程度のラフネスがあるはず
        assert roughness > 0.0

    def test_perfect_fifth(self):
        """完全5度の協和性"""
        roughness_p5 = calculate_consonance(edo=12, notes=[0, 7])
        roughness_unison = calculate_consonance(edo=12, notes=[0])
        roughness_m2 = calculate_consonance(edo=12, notes=[0, 1])

        # 完全5度は協和性においてユニゾンと短2度の間にあるべき
        assert roughness_unison < roughness_p5 < roughness_m2

    def test_deterministic_calculation(self):
        """同入力で同出力(決定的)であること"""
        roughness1 = calculate_consonance(edo=12, notes=[0, 4, 7])
        roughness2 = calculate_consonance(edo=12, notes=[0, 4, 7])

        # まったく同じであるべき(ランダム性なし)
        assert roughness1 == pytest.approx(roughness2)
