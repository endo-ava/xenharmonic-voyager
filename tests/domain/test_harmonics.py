"""倍音系列モデルのテスト"""

import numpy as np
import pytest

from src.domain.models import Harmonic, HarmonicSeries, SawtoothTimbre


class TestHarmonic:
    """Harmonicデータクラスのテスト"""

    def test_valid_harmonic(self):
        """有効な倍音の作成"""
        h = Harmonic(frequency=440.0, amplitude=1.0)
        assert h.frequency == 440.0
        assert h.amplitude == 1.0

    def test_invalid_frequency_zero(self):
        """周波数が0でValueErrorが発生"""
        with pytest.raises(ValueError, match="周波数は正である必要があります"):
            Harmonic(frequency=0.0, amplitude=1.0)

    def test_invalid_frequency_negative(self):
        """負の周波数でValueErrorが発生"""
        with pytest.raises(ValueError, match="周波数は正である必要があります"):
            Harmonic(frequency=-440.0, amplitude=1.0)

    def test_invalid_amplitude_negative(self):
        """負の振幅でValueErrorが発生"""
        with pytest.raises(ValueError, match=r"振幅は\[0, 1\]の範囲内である必要があります"):
            Harmonic(frequency=440.0, amplitude=-0.1)

    def test_invalid_amplitude_greater_than_one(self):
        """振幅が1より大きい場合にValueErrorが発生"""
        with pytest.raises(ValueError, match=r"振幅は\[0, 1\]の範囲内である必要があります"):
            Harmonic(frequency=440.0, amplitude=1.1)

    def test_amplitude_zero_is_valid(self):
        """振幅が0で有効"""
        h = Harmonic(frequency=440.0, amplitude=0.0)
        assert h.amplitude == 0.0

    def test_amplitude_one_is_valid(self):
        """振幅が1で有効"""
        h = Harmonic(frequency=440.0, amplitude=1.0)
        assert h.amplitude == 1.0

    def test_immutability(self):
        """Harmonicは不変"""
        h = Harmonic(frequency=440.0, amplitude=1.0)
        with pytest.raises(AttributeError):
            h.frequency = 880.0  # type: ignore


class TestHarmonicSeries:
    """HarmonicSeriesクラスのテスト"""

    def test_valid_series(self):
        """有効な倍音系列の作成"""
        harmonics = (
            Harmonic(frequency=440.0, amplitude=1.0),
            Harmonic(frequency=880.0, amplitude=0.5),
        )
        series = HarmonicSeries(harmonics=harmonics)
        assert len(series) == 2

    def test_empty_series_raises_error(self):
        """空の倍音系列でValueErrorが発生"""
        with pytest.raises(ValueError, match="少なくとも1つの倍音が含まれている必要があります"):
            HarmonicSeries(harmonics=())

    def test_get_frequencies(self):
        """周波数配列の抽出"""
        harmonics = (
            Harmonic(frequency=440.0, amplitude=1.0),
            Harmonic(frequency=880.0, amplitude=0.5),
            Harmonic(frequency=1320.0, amplitude=0.333),
        )
        series = HarmonicSeries(harmonics=harmonics)
        freqs = series.get_frequencies()

        expected = np.array([440.0, 880.0, 1320.0])
        np.testing.assert_allclose(freqs, expected)
        assert freqs.dtype == np.float64

    def test_get_amplitudes(self):
        """振幅配列の抽出"""
        harmonics = (
            Harmonic(frequency=440.0, amplitude=1.0),
            Harmonic(frequency=880.0, amplitude=0.5),
            Harmonic(frequency=1320.0, amplitude=0.333),
        )
        series = HarmonicSeries(harmonics=harmonics)
        amps = series.get_amplitudes()

        expected = np.array([1.0, 0.5, 0.333])
        np.testing.assert_allclose(amps, expected)
        assert amps.dtype == np.float64

    def test_len(self):
        """長さの計算"""
        harmonics = tuple(Harmonic(frequency=440.0 * k, amplitude=1.0 / k) for k in range(1, 11))
        series = HarmonicSeries(harmonics=harmonics)
        assert len(series) == 10

    def test_repr(self):
        """文字列表現"""
        harmonics = (
            Harmonic(frequency=440.0, amplitude=1.0),
            Harmonic(frequency=880.0, amplitude=0.5),
        )
        series = HarmonicSeries(harmonics=harmonics)
        repr_str = repr(series)

        assert "HarmonicSeries" in repr_str
        assert "num_harmonics=2" in repr_str

    def test_immutability(self):
        """HarmonicSeriesは不変"""
        harmonics = (Harmonic(frequency=440.0, amplitude=1.0),)
        series = HarmonicSeries(harmonics=harmonics)

        with pytest.raises(AttributeError):
            series.harmonics = ()  # type: ignore


class TestSawtoothTimbre:
    """SawtoothTimbreモデルのテスト"""

    def test_generate_harmonics_default_count(self):
        """デフォルト数(10)での倍音生成"""
        timbre = SawtoothTimbre()
        series = timbre.generate_harmonics(440.0)

        assert len(series) == 10

    def test_generate_harmonics_custom_count(self):
        """カスタム数での倍音生成"""
        timbre = SawtoothTimbre()
        series = timbre.generate_harmonics(440.0, num_harmonics=5)

        assert len(series) == 5

    def test_fundamental_frequency(self):
        """最初の倍音は基本周波数と一致"""
        timbre = SawtoothTimbre()
        series = timbre.generate_harmonics(440.0, num_harmonics=3)

        assert series.harmonics[0].frequency == pytest.approx(440.0)

    def test_harmonic_frequency_multiples(self):
        """倍音周波数は整数倍"""
        timbre = SawtoothTimbre()
        series = timbre.generate_harmonics(440.0, num_harmonics=5)

        expected_freqs = [440.0, 880.0, 1320.0, 1760.0, 2200.0]
        actual_freqs = [h.frequency for h in series.harmonics]

        np.testing.assert_allclose(actual_freqs, expected_freqs)

    def test_amplitude_decay_1_over_k(self):
        """振幅は1/kの減衰パターンに従う"""
        timbre = SawtoothTimbre()
        series = timbre.generate_harmonics(440.0, num_harmonics=10)

        # 期待される振幅:1、1/2、1/3、...、1/10
        expected_amps = [1.0 / k for k in range(1, 11)]
        actual_amps = [h.amplitude for h in series.harmonics]

        np.testing.assert_allclose(actual_amps, expected_amps, rtol=1e-9)

    def test_first_harmonic_amplitude_is_one(self):
        """基本周波数の振幅は1.0"""
        timbre = SawtoothTimbre()
        series = timbre.generate_harmonics(440.0, num_harmonics=5)

        assert series.harmonics[0].amplitude == pytest.approx(1.0)

    def test_second_harmonic_amplitude_is_half(self):
        """第2倍音の振幅は0.5"""
        timbre = SawtoothTimbre()
        series = timbre.generate_harmonics(440.0, num_harmonics=5)

        assert series.harmonics[1].amplitude == pytest.approx(0.5)

    def test_tenth_harmonic_amplitude(self):
        """第10倍音の振幅は0.1"""
        timbre = SawtoothTimbre()
        series = timbre.generate_harmonics(440.0, num_harmonics=10)

        assert series.harmonics[9].amplitude == pytest.approx(0.1)

    def test_different_fundamental_frequencies(self):
        """異なる基本周波数での生成"""
        timbre = SawtoothTimbre()

        # 220 Hzでテスト
        series_220 = timbre.generate_harmonics(220.0, num_harmonics=3)
        assert series_220.harmonics[0].frequency == pytest.approx(220.0)
        assert series_220.harmonics[1].frequency == pytest.approx(440.0)

        # 880 Hzでテスト
        series_880 = timbre.generate_harmonics(880.0, num_harmonics=3)
        assert series_880.harmonics[0].frequency == pytest.approx(880.0)
        assert series_880.harmonics[1].frequency == pytest.approx(1760.0)

    def test_invalid_fundamental_zero(self):
        """基本周波数が0でValueErrorが発生"""
        timbre = SawtoothTimbre()
        with pytest.raises(ValueError, match="基本周波数は正である必要があります"):
            timbre.generate_harmonics(0.0)

    def test_invalid_fundamental_negative(self):
        """負の基本周波数でValueErrorが発生"""
        timbre = SawtoothTimbre()
        with pytest.raises(ValueError, match="基本周波数は正である必要があります"):
            timbre.generate_harmonics(-440.0)

    def test_invalid_num_harmonics_zero(self):
        """num_harmonicsが0でValueErrorが発生"""
        timbre = SawtoothTimbre()
        with pytest.raises(ValueError, match="倍音の数は1以上である必要があります"):
            timbre.generate_harmonics(440.0, num_harmonics=0)

    def test_invalid_num_harmonics_negative(self):
        """負のnum_harmonicsでValueErrorが発生"""
        timbre = SawtoothTimbre()
        with pytest.raises(ValueError, match="倍音の数は1以上である必要があります"):
            timbre.generate_harmonics(440.0, num_harmonics=-1)

    def test_single_harmonic(self):
        """単一倍音(基本周波数のみ)の生成"""
        timbre = SawtoothTimbre()
        series = timbre.generate_harmonics(440.0, num_harmonics=1)

        assert len(series) == 1
        assert series.harmonics[0].frequency == pytest.approx(440.0)
        assert series.harmonics[0].amplitude == pytest.approx(1.0)

    def test_numpy_vectorization(self):
        """生成は内部でNumPy配列を使用"""
        timbre = SawtoothTimbre()
        series = timbre.generate_harmonics(440.0, num_harmonics=10)

        # get_frequenciesとget_amplitudesが配列を返すことを確認
        freqs = series.get_frequencies()
        amps = series.get_amplitudes()

        assert isinstance(freqs, np.ndarray)
        assert isinstance(amps, np.ndarray)

    def test_repr(self):
        """文字列表現"""
        timbre = SawtoothTimbre()
        repr_str = repr(timbre)

        assert "SawtoothTimbre" in repr_str
        assert "1/k" in repr_str
