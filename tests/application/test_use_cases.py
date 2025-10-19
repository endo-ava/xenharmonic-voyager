"""Application層（Use Case、DTO）のテスト"""

import pytest
from pydantic import ValidationError

from src.application.dto import ChordInput
from src.application.use_cases import CalculateConsonanceUseCase


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


class TestCalculateConsonanceUseCase:
    """協和性計算Use Caseのテストケース"""

    def test_execute_returns_consonance_result(self):
        """Use Case実行がConsonanceResultを返すこと"""
        use_case = CalculateConsonanceUseCase()
        result = use_case.execute(edo=12, notes=[0, 4, 7])
        assert hasattr(result, "total_roughness")
        assert isinstance(result.total_roughness, float)

    def test_execute_validates_input(self):
        """無効な入力でValidationErrorが発生すること"""
        use_case = CalculateConsonanceUseCase()
        with pytest.raises(ValidationError):
            use_case.execute(edo=12, notes=[0, 4, 12])

    def test_non_zero_result(self):
        """実際の和音で協和性計算が0以外の値を返すこと"""
        use_case = CalculateConsonanceUseCase()
        result = use_case.execute(edo=12, notes=[0, 4, 7])
        assert result.total_roughness > 0.0

    def test_unison_low_roughness(self):
        """ユニゾンは不協和音程より低いラフネスを持つこと"""
        use_case = CalculateConsonanceUseCase()
        result_unison = use_case.execute(edo=12, notes=[0])
        result_m2 = use_case.execute(edo=12, notes=[0, 1])
        assert result_unison.total_roughness < result_m2.total_roughness

    def test_minor_second_is_dissonant(self):
        """短2度は高いラフネス(低い協和性)を持つこと"""
        use_case = CalculateConsonanceUseCase()
        result_m2 = use_case.execute(edo=12, notes=[0, 1])
        result_p5 = use_case.execute(edo=12, notes=[0, 7])
        assert result_m2.total_roughness > result_p5.total_roughness

    def test_major_triad_moderate_roughness(self):
        """長三和音は音程間で中程度のラフネスを持つこと"""
        use_case = CalculateConsonanceUseCase()
        result_triad = use_case.execute(edo=12, notes=[0, 4, 7])
        result_unison = use_case.execute(edo=12, notes=[0])
        result_p5 = use_case.execute(edo=12, notes=[0, 7])
        assert result_unison.total_roughness < result_triad.total_roughness
        assert result_p5.total_roughness < result_triad.total_roughness

    def test_different_edo_systems(self):
        """異なるEDOシステムで計算が機能すること"""
        use_case = CalculateConsonanceUseCase()
        result_12edo = use_case.execute(edo=12, notes=[0, 4, 7])
        result_19edo = use_case.execute(edo=19, notes=[0, 6, 11])

        assert result_12edo.total_roughness > 0.0
        assert result_19edo.total_roughness > 0.0
        assert result_12edo.total_roughness != pytest.approx(result_19edo.total_roughness)

    def test_custom_base_frequency(self):
        """カスタム基本周波数は異なる結果を生成すること"""
        use_case = CalculateConsonanceUseCase()
        result_440 = use_case.execute(edo=12, notes=[0, 4, 7], base_frequency=440.0)
        result_220 = use_case.execute(edo=12, notes=[0, 4, 7], base_frequency=220.0)
        assert result_440.total_roughness != pytest.approx(result_220.total_roughness)

    def test_custom_num_harmonics(self):
        """異なるnum_harmonicsは異なる結果を生成すること"""
        use_case = CalculateConsonanceUseCase()
        result_5harm = use_case.execute(edo=12, notes=[0, 4, 7], num_harmonics=5)
        result_10harm = use_case.execute(edo=12, notes=[0, 4, 7], num_harmonics=10)
        assert result_5harm.total_roughness != pytest.approx(result_10harm.total_roughness)

    def test_single_note(self):
        """単一音符の計算"""
        use_case = CalculateConsonanceUseCase()
        result = use_case.execute(edo=12, notes=[0])
        assert result.total_roughness > 0.0

    def test_empty_notes_raises_error(self):
        """空の音符リストでValidationErrorが発生すること"""
        use_case = CalculateConsonanceUseCase()
        with pytest.raises(ValidationError):
            use_case.execute(edo=12, notes=[])

    def test_large_chord(self):
        """より大きな和音の計算"""
        use_case = CalculateConsonanceUseCase()
        result = use_case.execute(edo=12, notes=[0, 2, 4, 5, 7, 9])
        assert result.total_roughness > 0.0

    def test_deterministic_calculation(self):
        """同入力で同出力(決定的)であること"""
        use_case = CalculateConsonanceUseCase()
        result1 = use_case.execute(edo=12, notes=[0, 4, 7])
        result2 = use_case.execute(edo=12, notes=[0, 4, 7])
        assert result1.total_roughness == pytest.approx(result2.total_roughness)

    def test_result_metadata(self):
        """結果にメタデータが含まれること"""
        use_case = CalculateConsonanceUseCase()
        result = use_case.execute(edo=12, notes=[0, 4, 7])
        assert result.num_notes == 3
        assert result.num_harmonic_pairs > 0
        assert result.tuning_system.edo == 12

    def test_with_pair_details(self):
        """詳細データ付き計算"""
        use_case = CalculateConsonanceUseCase()
        result = use_case.execute(edo=12, notes=[0, 7], include_pair_details=True)
        assert result.pair_details is not None
        assert len(result.pair_details) > 0
