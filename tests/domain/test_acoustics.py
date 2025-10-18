"""音響的ラフネス計算のテスト"""

import pytest

from src.domain.acoustics import (
    calculate_dissonance_curve,
    calculate_roughness_pair,
    calculate_total_roughness,
    critical_bandwidth,
)
from src.domain.models import Harmonic


class TestCriticalBandwidth:
    """臨界帯域幅計算のテスト"""

    def test_critical_bandwidth_440hz(self):
        """A4(440 Hz)でのCB"""
        cb = critical_bandwidth(440.0)
        # CB = 0.24 * 440 + 25 = 105.6 + 25 = 130.6
        assert cb == pytest.approx(130.6)

    def test_critical_bandwidth_1000hz(self):
        """1000 HzでのCB"""
        cb = critical_bandwidth(1000.0)
        # CB = 0.24 * 1000 + 25 = 240 + 25 = 265
        assert cb == pytest.approx(265.0)

    def test_critical_bandwidth_100hz(self):
        """低周波数でのCB"""
        cb = critical_bandwidth(100.0)
        # CB = 0.24 * 100 + 25 = 24 + 25 = 49
        assert cb == pytest.approx(49.0)

    def test_critical_bandwidth_increases_with_frequency(self):
        """CBは周波数とともに単調に増加"""
        cb1 = critical_bandwidth(200.0)
        cb2 = critical_bandwidth(400.0)
        cb3 = critical_bandwidth(800.0)

        assert cb1 < cb2 < cb3

    def test_invalid_frequency_zero(self):
        """周波数が0でValueErrorが発生"""
        with pytest.raises(ValueError, match="周波数は正である必要があります"):
            critical_bandwidth(0.0)

    def test_invalid_frequency_negative(self):
        """負の周波数でValueErrorが発生"""
        with pytest.raises(ValueError, match="周波数は正である必要があります"):
            critical_bandwidth(-100.0)

    def test_cb_formula_consistency(self):
        """CBは線形公式に従う"""
        freq = 500.0
        cb = critical_bandwidth(freq)
        expected = 0.24 * freq + 25.0

        assert cb == pytest.approx(expected)


class TestDissonanceCurve:
    """Setharesの不協和曲線計算のテスト"""

    def test_unison_produces_zero_dissonance(self):
        """周波数差が0で不協和が0になること"""
        cb = critical_bandwidth(440.0)
        dissonance = calculate_dissonance_curve(0.0, cb)

        assert dissonance == pytest.approx(0.0, abs=1e-10)

    def test_large_separation_low_dissonance(self):
        """大きな周波数分離は低い不協和を持つ"""
        cb = critical_bandwidth(440.0)
        # 非常に大きな分離(複数のオクターブ)
        large_diff = cb * 10
        dissonance = calculate_dissonance_curve(large_diff, cb)

        # ゼロに近いはず(両方の指数関数がゼロに近づくため)
        assert dissonance == pytest.approx(0.0, abs=0.01)

    def test_peak_near_quarter_cb(self):
        """不協和が約0.25 * CBでピークに達すること"""
        cb = critical_bandwidth(440.0)

        # 様々な点での不協和を計算
        d_quarter = calculate_dissonance_curve(0.25 * cb, cb)
        d_eighth = calculate_dissonance_curve(0.125 * cb, cb)
        d_half = calculate_dissonance_curve(0.5 * cb, cb)

        # 0.25 * CBでの値は隣接する値よりも高くなるはず
        assert d_quarter > d_eighth
        assert d_quarter > d_half

    def test_curve_is_positive_near_peak(self):
        """不協和曲線はラフネス領域で正"""
        cb = critical_bandwidth(440.0)

        for fraction in [0.1, 0.2, 0.3, 0.4, 0.5]:
            dissonance = calculate_dissonance_curve(fraction * cb, cb)
            assert dissonance > 0.0

    def test_invalid_negative_frequency_difference(self):
        """負の周波数差でValueErrorが発生"""
        cb = critical_bandwidth(440.0)
        with pytest.raises(ValueError, match="非負である必要があります"):
            calculate_dissonance_curve(-10.0, cb)

    def test_invalid_zero_critical_band(self):
        """CBが0でValueErrorが発生"""
        with pytest.raises(ValueError, match="臨界帯域は正である必要があります"):
            calculate_dissonance_curve(10.0, 0.0)

    def test_invalid_negative_critical_band(self):
        """負のCBでValueErrorが発生"""
        with pytest.raises(ValueError, match="臨界帯域は正である必要があります"):
            calculate_dissonance_curve(10.0, -100.0)

    def test_custom_b_parameters(self):
        """カスタムb1, b2パラメータでの不協和曲線"""
        cb = critical_bandwidth(440.0)
        freq_diff = 20.0

        # デフォルトパラメータ
        d_default = calculate_dissonance_curve(freq_diff, cb)

        # カスタムパラメータ(異なる結果を生成するはず)
        d_custom = calculate_dissonance_curve(freq_diff, cb, b1=2.0, b2=4.0)

        assert d_default != pytest.approx(d_custom)


class TestRoughnessPair:
    """2倍音間のラフネス計算テスト"""

    def test_unison_zero_roughness(self):
        """同一周波数は0のラフネスを生成"""
        h1 = Harmonic(frequency=440.0, amplitude=1.0)
        h2 = Harmonic(frequency=440.0, amplitude=1.0)

        result = calculate_roughness_pair(h1, h2)

        assert result.roughness == pytest.approx(0.0, abs=1e-10)

    def test_octave_low_roughness(self):
        """オクターブ間隔は低いラフネスを持つ"""
        h1 = Harmonic(frequency=440.0, amplitude=1.0)
        h2 = Harmonic(frequency=880.0, amplitude=1.0)  # 完全オクターブ

        result = calculate_roughness_pair(h1, h2)

        # オクターブは非常に低いラフネスを持つべき(大きな周波数分離)
        assert result.roughness < 0.05  # 経験的しきい値

    def test_minor_second_high_roughness(self):
        """短2度は高いラフネスを持つ"""
        h1 = Harmonic(frequency=440.0, amplitude=1.0)
        h2 = Harmonic(frequency=466.16, amplitude=1.0)  # 短2度(AからA#)

        result_m2 = calculate_roughness_pair(h1, h2)

        # オクターブと比較
        h3 = Harmonic(frequency=880.0, amplitude=1.0)
        result_octave = calculate_roughness_pair(h1, h3)

        # 短2度はオクターブよりも大幅に多くのラフネスを持つべき
        assert result_m2.roughness > result_octave.roughness * 2

    def test_amplitude_weighting(self):
        """ラフネスは振幅の積に比例"""
        h1 = Harmonic(frequency=440.0, amplitude=1.0)
        h2 = Harmonic(frequency=450.0, amplitude=1.0)

        result_full = calculate_roughness_pair(h1, h2)

        # 第2倍音の半分の振幅
        h2_half = Harmonic(frequency=450.0, amplitude=0.5)
        result_half = calculate_roughness_pair(h1, h2_half)

        # ラフネスは約半分になるはず
        assert result_half.roughness == pytest.approx(result_full.roughness * 0.5, rel=1e-6)

    def test_symmetry(self):
        """ラフネスは対称:R(h1, h2) = R(h2, h1)"""
        h1 = Harmonic(frequency=440.0, amplitude=1.0)
        h2 = Harmonic(frequency=554.37, amplitude=0.8)

        result_12 = calculate_roughness_pair(h1, h2)
        result_21 = calculate_roughness_pair(h2, h1)

        assert result_12.roughness == pytest.approx(result_21.roughness, rel=1e-9)

    def test_zero_amplitude_zero_roughness(self):
        """振幅0はラフネス0を生成"""
        h1 = Harmonic(frequency=440.0, amplitude=0.0)
        h2 = Harmonic(frequency=450.0, amplitude=1.0)

        result = calculate_roughness_pair(h1, h2)

        assert result.roughness == pytest.approx(0.0, abs=1e-10)

    def test_both_zero_amplitude(self):
        """両振幅0はラフネス0を生成"""
        h1 = Harmonic(frequency=440.0, amplitude=0.0)
        h2 = Harmonic(frequency=450.0, amplitude=0.0)

        result = calculate_roughness_pair(h1, h2)

        assert result.roughness == pytest.approx(0.0, abs=1e-10)

    def test_perfect_fifth_moderate_roughness(self):
        """完全5度は中程度のラフネスを持つ"""
        h1 = Harmonic(frequency=440.0, amplitude=1.0)
        h2 = Harmonic(frequency=659.25, amplitude=1.0)  # 完全5度

        result_p5 = calculate_roughness_pair(h1, h2)

        # 完全5度:低いがゼロではないラフネス
        h_octave = Harmonic(frequency=880.0, amplitude=1.0)
        result_octave = calculate_roughness_pair(h1, h_octave)

        h_minor2 = Harmonic(frequency=466.16, amplitude=1.0)
        result_minor2 = calculate_roughness_pair(h1, h_minor2)

        # 完全5度はオクターブと短2度の間にあるべき
        assert result_octave.roughness < result_p5.roughness < result_minor2.roughness

    def test_uses_lower_frequency_cb(self):
        """CB計算は2周波数のうち低い方を使用"""
        # これは実装では暗黙的だが、動作を検証できる
        h_low = Harmonic(frequency=100.0, amplitude=1.0)
        h_high = Harmonic(frequency=200.0, amplitude=1.0)

        result = calculate_roughness_pair(h_low, h_high)

        # 順序に関係なく同じであるべき(対称性)
        result_reversed = calculate_roughness_pair(h_high, h_low)

        assert result.roughness == pytest.approx(result_reversed.roughness, rel=1e-9)


class TestTotalRoughness:
    """複数ペアの総ラフネス計算テスト"""

    def test_empty_pairs_zero_roughness(self):
        """空リストはラフネス0を返す"""
        roughness = calculate_total_roughness([])
        assert roughness == pytest.approx(0.0)

    def test_single_pair(self):
        """単一ペアの総ラフネス"""
        h1 = Harmonic(frequency=440.0, amplitude=1.0)
        h2 = Harmonic(frequency=450.0, amplitude=1.0)

        result = calculate_roughness_pair(h1, h2)
        total_roughness = calculate_total_roughness([(h1, h2)])

        assert total_roughness == pytest.approx(result.roughness)

    def test_multiple_pairs_sum(self):
        """総ラフネスは個別ラフネスの合計"""
        h1 = Harmonic(frequency=440.0, amplitude=1.0)
        h2 = Harmonic(frequency=450.0, amplitude=1.0)
        h3 = Harmonic(frequency=460.0, amplitude=1.0)

        r12 = calculate_roughness_pair(h1, h2).roughness
        r13 = calculate_roughness_pair(h1, h3).roughness
        r23 = calculate_roughness_pair(h2, h3).roughness

        pairs = [(h1, h2), (h1, h3), (h2, h3)]
        total = calculate_total_roughness(pairs)

        expected_total = r12 + r13 + r23

        assert total == pytest.approx(expected_total, rel=1e-9)

    def test_triad_roughness(self):
        """音楽的な三和音の総ラフネス"""
        # A4から始まる12-EDO長三和音
        h1 = Harmonic(frequency=440.0, amplitude=1.0)  # A4
        h2 = Harmonic(frequency=554.37, amplitude=1.0)  # C#5(長3度)
        h3 = Harmonic(frequency=659.25, amplitude=1.0)  # E5(完全5度)

        pairs = [(h1, h2), (h1, h3), (h2, h3)]
        total = calculate_total_roughness(pairs)

        # 合計は正であるべき(ある程度のラフネス)
        assert total > 0.0

        # 合計は3つのペアのラフネスの合計であるべき
        assert total == pytest.approx(
            calculate_roughness_pair(h1, h2).roughness
            + calculate_roughness_pair(h1, h3).roughness
            + calculate_roughness_pair(h2, h3).roughness,
            rel=1e-9,
        )
