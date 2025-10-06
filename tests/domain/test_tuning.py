"""TuningSystemクラスのテスト"""

import numpy as np
import pytest

from src.domain.tuning import TuningSystem


class TestTuningSystemValidation:
    """TuningSystem初期化の検証ロジック"""

    def test_valid_tuning_system_12edo(self):
        """有効な12-EDOシステムが正しく作成されること"""
        tuning = TuningSystem(edo=12, base_frequency=440.0)
        assert tuning.edo == 12
        assert tuning.base_frequency == 440.0

    def test_valid_tuning_system_19edo(self):
        """有効な19-EDOシステムが正しく作成されること"""
        tuning = TuningSystem(edo=19, base_frequency=440.0)
        assert tuning.edo == 19
        assert tuning.base_frequency == 440.0

    def test_default_base_frequency(self):
        """デフォルト基本周波数は440 Hz"""
        tuning = TuningSystem(edo=12)
        assert tuning.base_frequency == 440.0

    def test_invalid_edo_zero(self):
        """EDOが0でValueErrorが発生"""
        with pytest.raises(ValueError, match="EDOは正である必要があります"):
            TuningSystem(edo=0)

    def test_invalid_edo_negative(self):
        """負のEDOでValueErrorが発生"""
        with pytest.raises(ValueError, match="EDOは正である必要があります"):
            TuningSystem(edo=-1)

    def test_invalid_base_frequency_zero(self):
        """基本周波数が0でValueErrorが発生"""
        with pytest.raises(ValueError, match="基本周波数は正である必要があります"):
            TuningSystem(edo=12, base_frequency=0.0)

    def test_invalid_base_frequency_negative(self):
        """負の基本周波数でValueErrorが発生"""
        with pytest.raises(ValueError, match="基本周波数は正である必要があります"):
            TuningSystem(edo=12, base_frequency=-440.0)


class TestGetFrequency:
    """個別ステップの周波数計算テスト"""

    def test_step_zero_returns_base_frequency(self):
        """ステップ0は基本周波数を返す"""
        tuning = TuningSystem(edo=12, base_frequency=440.0)
        assert tuning.get_frequency(0) == 440.0

    def test_octave_up_doubles_frequency(self):
        """1オクターブ上(Nステップ)は周波数を2倍にする"""
        tuning = TuningSystem(edo=12, base_frequency=440.0)
        # 12-EDOのステップ12は1オクターブ上
        assert tuning.get_frequency(12) == pytest.approx(880.0)

    def test_octave_down_halves_frequency(self):
        """1オクターブ下は周波数を半分にする"""
        tuning = TuningSystem(edo=12, base_frequency=440.0)
        # 12-EDOのステップ-12は1オクターブ下
        assert tuning.get_frequency(-12) == pytest.approx(220.0)

    def test_perfect_fifth_12edo(self):
        """12-EDOの完全5度(7半音)"""
        tuning = TuningSystem(edo=12, base_frequency=440.0)
        # 完全5度は12-EDOで7半音
        # 期待値:440 * 2^(7/12) ≈ 659.255 Hz
        assert tuning.get_frequency(7) == pytest.approx(659.2551138257401, rel=1e-9)

    def test_major_third_12edo(self):
        """12-EDOの長3度(4半音)"""
        tuning = TuningSystem(edo=12, base_frequency=440.0)
        # 長3度は12-EDOで4半音
        # 期待値:440 * 2^(4/12) ≈ 554.365 Hz
        assert tuning.get_frequency(4) == pytest.approx(554.3652619537442, rel=1e-9)

    def test_19edo_step_calculation(self):
        """19-EDOでの周波数計算"""
        tuning = TuningSystem(edo=19, base_frequency=440.0)
        # 19-EDOのステップ1
        # 期待値:440 * 2^(1/19) ≈ 456.348 Hz
        assert tuning.get_frequency(1) == pytest.approx(456.3482195563244, rel=1e-9)

    def test_multiple_octaves_up(self):
        """複数オクターブ上の計算"""
        tuning = TuningSystem(edo=12, base_frequency=440.0)
        # 2オクターブ上(24半音)
        assert tuning.get_frequency(24) == pytest.approx(1760.0)

    def test_fractional_step_behavior(self):
        """公式が与えられたステップで正しく機能すること"""
        tuning = TuningSystem(edo=12, base_frequency=440.0)
        # 任意のステップn:f = 440 * 2^(n/12)
        step = 5
        expected = 440.0 * (2.0 ** (step / 12))
        assert tuning.get_frequency(step) == pytest.approx(expected)


class TestGetIntervalCents:
    """セント単位でのインターバル計算テスト"""

    def test_semitone_in_12edo(self):
        """12-EDOの1半音は100セント"""
        tuning = TuningSystem(edo=12)
        assert tuning.get_interval_cents(1) == pytest.approx(100.0)

    def test_octave_equals_1200_cents(self):
        """1オクターブは1200セント"""
        tuning = TuningSystem(edo=12)
        assert tuning.get_interval_cents(12) == pytest.approx(1200.0)

    def test_perfect_fifth_12edo_cents(self):
        """12-EDOの完全5度は700セント"""
        tuning = TuningSystem(edo=12)
        # 7半音= 700セント
        assert tuning.get_interval_cents(7) == pytest.approx(700.0)

    def test_19edo_step_cents(self):
        """19-EDOの1ステップ"""
        tuning = TuningSystem(edo=19)
        # 19-EDOの1ステップ= 1200/19 ≈ 63.158セント
        assert tuning.get_interval_cents(1) == pytest.approx(63.15789473684211, rel=1e-9)

    def test_19edo_octave_cents(self):
        """19-EDOの19ステップは1200セント"""
        tuning = TuningSystem(edo=19)
        assert tuning.get_interval_cents(19) == pytest.approx(1200.0)

    def test_negative_interval(self):
        """負のインターバル(下降)"""
        tuning = TuningSystem(edo=12)
        assert tuning.get_interval_cents(-12) == pytest.approx(-1200.0)


class TestGetFrequenciesForChord:
    """和音のバッチ周波数計算テスト"""

    def test_major_triad_12edo(self):
        """12-EDO長三和音[0, 4, 7]の周波数"""
        tuning = TuningSystem(edo=12, base_frequency=440.0)
        freqs = tuning.get_frequencies_for_chord([0, 4, 7])

        expected = np.array(
            [
                440.0,  # A4
                554.3652619537442,  # C#5(長3度)
                659.2551138257401,  # E5(完全5度)
            ]
        )

        np.testing.assert_allclose(freqs, expected, rtol=1e-9)

    def test_minor_triad_12edo(self):
        """12-EDO短三和音[0, 3, 7]の周波数"""
        tuning = TuningSystem(edo=12, base_frequency=440.0)
        freqs = tuning.get_frequencies_for_chord([0, 3, 7])

        expected = np.array(
            [
                440.0,  # A4
                523.2511306011972,  # C5(短3度)
                659.2551138257401,  # E5(完全5度)
            ]
        )

        np.testing.assert_allclose(freqs, expected, rtol=1e-9)

    def test_empty_chord(self):
        """空の和音は空の配列を返す"""
        tuning = TuningSystem(edo=12, base_frequency=440.0)
        freqs = tuning.get_frequencies_for_chord([])
        assert len(freqs) == 0

    def test_single_note(self):
        """単一音符は単一の周波数を返す"""
        tuning = TuningSystem(edo=12, base_frequency=440.0)
        freqs = tuning.get_frequencies_for_chord([7])

        expected = np.array([659.2551138257401])
        np.testing.assert_allclose(freqs, expected, rtol=1e-9)

    def test_19edo_chord(self):
        """19-EDOでの和音計算"""
        tuning = TuningSystem(edo=19, base_frequency=440.0)
        freqs = tuning.get_frequencies_for_chord([0, 8, 11])

        # 期待される周波数を計算
        expected = np.array(
            [
                440.0 * (2.0 ** (0 / 19)),
                440.0 * (2.0 ** (8 / 19)),
                440.0 * (2.0 ** (11 / 19)),
            ]
        )

        np.testing.assert_allclose(freqs, expected, rtol=1e-9)

    def test_return_type_is_numpy_array(self):
        """戻り値の型はNumPy配列"""
        tuning = TuningSystem(edo=12, base_frequency=440.0)
        freqs = tuning.get_frequencies_for_chord([0, 4, 7])
        assert isinstance(freqs, np.ndarray)


class TestRepr:
    """文字列表現のテスト"""

    def test_repr_format(self):
        """reprはEDOと基本周波数を含む"""
        tuning = TuningSystem(edo=12, base_frequency=440.0)
        repr_str = repr(tuning)

        assert "TuningSystem" in repr_str
        assert "edo=12" in repr_str
        assert "base_frequency=440.00 Hz" in repr_str

    def test_repr_with_different_frequency(self):
        """非標準の基本周波数でのrepr"""
        tuning = TuningSystem(edo=19, base_frequency=432.0)
        repr_str = repr(tuning)

        assert "edo=19" in repr_str
        assert "432.00 Hz" in repr_str
