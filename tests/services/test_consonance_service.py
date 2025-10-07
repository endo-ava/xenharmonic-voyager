"""協和性計算サービスのテスト"""

import pytest

from src.domain.harmonics import SawtoothTimbre
from src.domain.tuning import TuningSystem
from src.services.consonance_service import ConsonanceCalculator, ConsonanceResult


class TestConsonanceResult:
    """ConsonanceResultデータクラスのテスト"""

    def test_valid_result(self):
        """有効なConsonanceResultの作成"""
        tuning = TuningSystem(edo=12, base_frequency=440.0)
        result = ConsonanceResult(
            total_roughness=1.234,
            num_notes=3,
            num_harmonic_pairs=135,
            tuning_system=tuning,
        )

        assert result.total_roughness == pytest.approx(1.234)
        assert result.num_notes == 3
        assert result.num_harmonic_pairs == 135
        assert result.tuning_system.edo == 12

    def test_immutability(self):
        """ConsonanceResultが不変であること"""
        tuning = TuningSystem(edo=12, base_frequency=440.0)
        result = ConsonanceResult(
            total_roughness=1.0,
            num_notes=2,
            num_harmonic_pairs=45,
            tuning_system=tuning,
        )

        with pytest.raises(AttributeError):
            result.total_roughness = 2.0  # type: ignore


class TestConsonanceCalculator:
    """ConsonanceCalculatorサービスのテスト"""

    def test_initialization_valid(self):
        """有効なパラメータでの計算機の初期化"""
        tuning = TuningSystem(edo=12, base_frequency=440.0)
        timbre = SawtoothTimbre()

        calculator = ConsonanceCalculator(
            tuning_system=tuning,
            timbre_model=timbre,
            num_harmonics=10,
        )

        assert calculator.tuning_system.edo == 12
        assert calculator.num_harmonics == 10
        assert isinstance(calculator.timbre_model, SawtoothTimbre)

    def test_initialization_default_harmonics(self):
        """デフォルトのnum_harmonicsでの計算機の初期化"""
        tuning = TuningSystem(edo=12, base_frequency=440.0)
        timbre = SawtoothTimbre()

        calculator = ConsonanceCalculator(
            tuning_system=tuning,
            timbre_model=timbre,
        )

        assert calculator.num_harmonics == 10

    def test_invalid_num_harmonics_zero(self):
        """num_harmonics=0でValueErrorが発生"""
        tuning = TuningSystem(edo=12, base_frequency=440.0)
        timbre = SawtoothTimbre()

        with pytest.raises(ValueError, match="num_harmonicsは1以上である必要があります"):
            ConsonanceCalculator(
                tuning_system=tuning,
                timbre_model=timbre,
                num_harmonics=0,
            )

    def test_invalid_num_harmonics_negative(self):
        """負のnum_harmonicsでValueErrorが発生"""
        tuning = TuningSystem(edo=12, base_frequency=440.0)
        timbre = SawtoothTimbre()

        with pytest.raises(ValueError, match="num_harmonicsは1以上である必要があります"):
            ConsonanceCalculator(
                tuning_system=tuning,
                timbre_model=timbre,
                num_harmonics=-1,
            )

    def test_empty_chord_raises_error(self):
        """空のchord_stepsでValueErrorが発生"""
        tuning = TuningSystem(edo=12, base_frequency=440.0)
        timbre = SawtoothTimbre()
        calculator = ConsonanceCalculator(tuning, timbre, num_harmonics=10)

        with pytest.raises(ValueError, match="chord_stepsを空にすることはできません"):
            calculator.calculate_consonance([])

    def test_single_note_has_roughness_from_harmonics(self):
        """単一の音符でもその倍音同士の干渉によりラフネスが発生する"""
        tuning = TuningSystem(edo=12, base_frequency=440.0)
        timbre = SawtoothTimbre()
        calculator = ConsonanceCalculator(tuning, timbre, num_harmonics=10)

        result = calculator.calculate_consonance([0])  # Single A4

        # 単一の音符:10個の倍音がありますが、ペアはi < jなので、最初の倍音は
        # 他の9つとペアになります= 9ペア、2番目は他の8つと= 8ペアなど。
        # 合計 = 9+8+7+6+5+4+3+2+1 = 45ペア
        assert result.num_notes == 1
        assert result.num_harmonic_pairs == 45
        # すべてのペアは同じ基本周波数からなので、ある程度のラフネスが予想されます
        assert result.total_roughness > 0.0

    def test_octave_low_roughness(self):
        """完全オクターブは低いラフネスを持つ"""
        tuning = TuningSystem(edo=12, base_frequency=440.0)
        timbre = SawtoothTimbre()
        calculator = ConsonanceCalculator(tuning, timbre, num_harmonics=5)

        # オクターブ:12-EDOで12半音
        result = calculator.calculate_consonance([0, 12])

        # 2音符*各5倍音=合計10倍音
        # ペア:10 choose 2 = 45ペア
        assert result.num_notes == 2
        assert result.num_harmonic_pairs == 45

        # オクターブは非常に協和的であるべき(低いラフネス)
        # 正確な値は倍音に依存しますが、比較的に低いはず
        assert result.total_roughness < 2.0  # 経験的しきい値

    def test_minor_second_high_roughness(self):
        """短2度は高いラフネスを持つ"""
        tuning = TuningSystem(edo=12, base_frequency=440.0)
        timbre = SawtoothTimbre()
        calculator = ConsonanceCalculator(tuning, timbre, num_harmonics=5)

        # 短2度:12-EDOで1半音
        result_m2 = calculator.calculate_consonance([0, 1])

        # オクターブと比較
        result_octave = calculator.calculate_consonance([0, 12])

        # 短2度はオクターブよりも大幅に多くのラフネスを持つべき
        assert result_m2.total_roughness > result_octave.total_roughness * 2

    def test_major_triad_moderate_roughness(self):
        """12-EDOの長三和音は中程度のラフネスを持つ"""
        tuning = TuningSystem(edo=12, base_frequency=440.0)
        timbre = SawtoothTimbre()
        calculator = ConsonanceCalculator(tuning, timbre, num_harmonics=5)

        # C長三和音:根音(0)、長3度(4)、完全5度(7)
        result = calculator.calculate_consonance([0, 4, 7])

        # 3音符*各5倍音=合計15倍音
        # ペア:15 choose 2 = 105ペア
        assert result.num_notes == 3
        assert result.num_harmonic_pairs == 105

        # 長三和音は正であるが中程度のラフネスを持つべき
        assert result.total_roughness > 0.0
        # 短2度よりもラフネスが低いはず
        result_m2 = calculator.calculate_consonance([0, 1])
        assert result.total_roughness < result_m2.total_roughness

    def test_different_edo_systems(self):
        """異なるN-EDOチューニングシステムでの計算"""
        timbre = SawtoothTimbre()

        # 12-EDO長三和音
        calc_12edo = ConsonanceCalculator(
            TuningSystem(edo=12, base_frequency=440.0),
            timbre,
            num_harmonics=5,
        )
        result_12 = calc_12edo.calculate_consonance([0, 4, 7])

        # 19-EDO「長」三和音(近似:0、6、11)
        # 19-EDOは12-EDOよりも優れた長3度近似を持つ
        calc_19edo = ConsonanceCalculator(
            TuningSystem(edo=19, base_frequency=440.0),
            timbre,
            num_harmonics=5,
        )
        result_19 = calc_19edo.calculate_consonance([0, 6, 11])

        # 両方とも有効な結果を生成するはず
        assert result_12.total_roughness > 0.0
        assert result_19.total_roughness > 0.0

        # 結果は異なるはず(異なるチューニングシステム)
        assert result_12.total_roughness != pytest.approx(result_19.total_roughness)

    def test_num_harmonic_pairs_formula(self):
        """num_harmonic_pairsが組み合わせ式に従うこと"""
        tuning = TuningSystem(edo=12, base_frequency=440.0)
        timbre = SawtoothTimbre()

        # 2音符、各5倍音=合計10倍音
        # ペア = 10 choose 2 = 10! / (2! * 8!) = 45
        calculator = ConsonanceCalculator(tuning, timbre, num_harmonics=5)
        result = calculator.calculate_consonance([0, 12])
        assert result.num_harmonic_pairs == 45

        # 3音符、各5倍音=合計15倍音
        # ペア = 15 choose 2 = 15! / (2! * 13!) = 105
        result = calculator.calculate_consonance([0, 4, 7])
        assert result.num_harmonic_pairs == 105

        # 4音符、各3倍音=合計12倍音
        # ペア = 12 choose 2 = 66
        calculator = ConsonanceCalculator(tuning, timbre, num_harmonics=3)
        result = calculator.calculate_consonance([0, 3, 7, 10])  # ドミナント7th
        assert result.num_harmonic_pairs == 66

    def test_result_includes_tuning_system_reference(self):
        """結果にチューニングシステムへの参照が含まれていること"""
        tuning = TuningSystem(edo=19, base_frequency=440.0)
        timbre = SawtoothTimbre()
        calculator = ConsonanceCalculator(tuning, timbre, num_harmonics=5)

        result = calculator.calculate_consonance([0, 6])

        assert result.tuning_system.edo == 19
        assert result.tuning_system.base_frequency == pytest.approx(440.0)

    def test_different_num_harmonics(self):
        """異なるnum_harmonicsは異なる結果を生成すること"""
        tuning = TuningSystem(edo=12, base_frequency=440.0)
        timbre = SawtoothTimbre()

        calc_5harm = ConsonanceCalculator(tuning, timbre, num_harmonics=5)
        calc_10harm = ConsonanceCalculator(tuning, timbre, num_harmonics=10)

        result_5 = calc_5harm.calculate_consonance([0, 4, 7])
        result_10 = calc_10harm.calculate_consonance([0, 4, 7])

        # より多くの倍音=より多くのペア=異なるラフネス
        assert result_5.num_harmonic_pairs != result_10.num_harmonic_pairs
        assert result_5.total_roughness != pytest.approx(result_10.total_roughness)

    def test_properties(self):
        """計算機のプロパティが正しい値を返すこと"""
        tuning = TuningSystem(edo=12, base_frequency=440.0)
        timbre = SawtoothTimbre()
        calculator = ConsonanceCalculator(tuning, timbre, num_harmonics=7)

        assert calculator.tuning_system is tuning
        assert calculator.timbre_model is timbre
        assert calculator.num_harmonics == 7

    def test_large_chord(self):
        """より大きな和音の計算"""
        tuning = TuningSystem(edo=12, base_frequency=440.0)
        timbre = SawtoothTimbre()
        calculator = ConsonanceCalculator(tuning, timbre, num_harmonics=3)

        # 6音の和音
        result = calculator.calculate_consonance([0, 2, 4, 5, 7, 9])

        # 6音符*3倍音=合計18倍音
        # ペア = 18 choose 2 = 153
        assert result.num_notes == 6
        assert result.num_harmonic_pairs == 153
        assert result.total_roughness > 0.0

    def test_unison_with_harmonics(self):
        """ユニゾン(同音2回)が期待どおりに動作すること"""
        tuning = TuningSystem(edo=12, base_frequency=440.0)
        timbre = SawtoothTimbre()
        calculator = ConsonanceCalculator(tuning, timbre, num_harmonics=5)

        # 2つの同一の音符(ユニゾン)
        result = calculator.calculate_consonance([0, 0])

        # 2音符*5倍音=合計10倍音
        # しかし、周波数が同一であるため、倍音が重複します
        # これにより、Δf = 0の(h1_note1、h1_note2)のようなペアが作成されます
        assert result.num_notes == 2
        assert result.num_harmonic_pairs == 45

        # ユニゾンペア(Δf = 0)はラフネスに0貢献します
        # しかし、クロスハーモニックペア(例:h1対h2)はまだラフネスを持っています
        assert result.total_roughness > 0.0
