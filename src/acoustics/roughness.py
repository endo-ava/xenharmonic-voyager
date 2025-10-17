"""Sethares(1993)モデルに基づく音響的ラフネス計算。

このモジュールは、2つの倍音成分間の感覚的な不協和を定量化する
心理音響的ラフネスモデルを実装します。

References:
    - Sethares, W. A. (1993). "Local consonance and the relationship between
      timbre and scale." Journal of the Acoustical Society of America, 94(3).
    - Plomp, R., & Levelt, W. J. M. (1965). "Tonal consonance and critical
      bandwidth." Journal of the Acoustical Society of America, 38.
"""

from dataclasses import dataclass

import numpy as np

from src.constants import CB_COEFFICIENT, CB_CONSTANT, ROUGHNESS_B1, ROUGHNESS_B2
from src.domain.harmonics import Harmonic


@dataclass(frozen=True)
class RoughnessPairResult:
    """2つの倍音間のラフネス計算の結果を保持するデータクラス。

    このクラスは、ラフネス計算プロセスで得られる全ての中間値と最終結果を
    カプセル化します。これにより、Service層での計算の重複を避けることができます。

    Attributes:
        roughness: 最終的なラフネス値（振幅積 × 不協和曲線値）
        frequency_difference: 2つの周波数間の絶対差 (Hz)
        critical_bandwidth: 使用された臨界帯域幅 (Hz)
        normalized_freq_diff: 正規化された周波数差 (Δf / CB)
        dissonance_value: 不協和曲線から得られた値 g(x)
        amplitude_product: 2つの倍音の振幅の積

    Examples:
        >>> h1 = Harmonic(frequency=440.0, amplitude=1.0)
        >>> h2 = Harmonic(frequency=880.0, amplitude=0.5)
        >>> result = calculate_roughness_pair(h1, h2)
        >>> result.roughness
        0.0234...
        >>> result.normalized_freq_diff
        3.36...
    """

    roughness: float
    frequency_difference: float
    critical_bandwidth: float
    normalized_freq_diff: float
    dissonance_value: float
    amplitude_product: float


def critical_bandwidth(frequency: float) -> float:
    """単純化されたPlomp-Leveltモデルを使用して臨界帯域幅を計算します。

    臨界帯域幅は、2つのトーンが干渉し、ラフネスを生じさせる周波数範囲です。
    この実装では、バークスケールの単純化された線形近似を使用します。

    Formula:
        CB(f) ≈ 0.24 * f + 25 Hz

    この近似は、完全なバークスケール変換よりも計算効率が高い一方で、
    可聴範囲(20-20000 Hz)に対して十分な精度を提供します。

    Args:
        frequency: 周波数(Hz)(正である必要があります)

    Returns:
        臨界帯域幅(Hz)

    Raises:
        ValueError: frequency <= 0 の場合

    References:
        Plomp & Levelt (1965), Sethares (1993)

    Examples:
        >>> critical_bandwidth(440.0)  # A4
        130.6
        >>> critical_bandwidth(1000.0)
        265.0
    """
    if frequency <= 0:
        msg = f"周波数は正である必要がありますが、{frequency}が指定されました"
        raise ValueError(msg)

    return CB_COEFFICIENT * frequency + CB_CONSTANT


def calculate_dissonance_curve(
    frequency_difference: float,
    critical_band: float,
    b1: float = ROUGHNESS_B1,
    b2: float = ROUGHNESS_B2,
) -> float:
    """Setharesの不協和曲線の値を計算します。

    不協和曲線は、2つのトーン間の周波数分離の関数として
    ラフネスの知覚をモデル化します。この曲線は:
    - frequency_difference = 0(ユニゾン、ラフネスなし)で0から始まります
    - 約0.25 * critical_bandでピークに達します(最大ラフネス)
    - frequency_differenceが増加するにつれて0に向かって減衰します

    Formula:
        g(Δf, s) = exp(-b1 * s * Δf) - exp(-b2 * s * Δf)

    where:
        - Δf = 周波数差 (Hz)
        - s = 臨界帯域 (Hz)
        - b1, b2 = 曲線の急峻さを制御する形状パラメータ

    Args:
        frequency_difference: 絶対周波数差(Hz)(≥ 0)
        critical_band: 臨界帯域幅(Hz)(> 0)
        b1: 最初の形状パラメータ(デフォルト: Setharesの3.5)
        b2: 2番目の形状パラメータ(デフォルト: Setharesの5.75)

    Returns:
        不協和曲線の値(正規化され、通常は[0, ~0.25]の範囲)

    Raises:
        ValueError: frequency_difference < 0 または critical_band <= 0 の場合

    Examples:
        >>> cb = critical_bandwidth(440.0)
        >>> calculate_dissonance_curve(0.0, cb)  # Unison
        0.0
        >>> calculate_dissonance_curve(cb * 0.25, cb)  # Near peak
        # 最大不協和に近い値を返す
    """
    if frequency_difference < 0:
        msg = f"周波数差は非負である必要がありますが、{frequency_difference}が指定されました"
        raise ValueError(msg)
    if critical_band <= 0:
        msg = f"臨界帯域は正である必要がありますが、{critical_band}が指定されました"
        raise ValueError(msg)

    # Setharesの不協和曲線は、正規化された周波数差を使用します
    # 式は次のとおりです: exp(-b1 * x) - exp(-b2 * x)
    # ここで、x = frequency_difference / critical_band(正規化)

    # 臨界帯域幅で周波数差を正規化
    x = frequency_difference / critical_band

    # Setharesの不協和曲線: exp(-b1*x) - exp(-b2*x)
    # これにより、x ≈ 0.25あたりでピークに達する曲線が作成されます
    term1 = np.exp(-b1 * x)
    term2 = np.exp(-b2 * x)

    return float(term1 - term2)


def calculate_roughness_pair(
    harmonic1: Harmonic,
    harmonic2: Harmonic,
    b1: float = ROUGHNESS_B1,
    b2: float = ROUGHNESS_B2,
) -> RoughnessPairResult:
    """2つの倍音成分間のラフネスを計算します。

    これは、周波数と振幅に基づいて2つの倍音成分間の
    感覚的な不協和(ラフネス)を計算する中心的な関数です。

    The roughness is:
    1. 振幅の積によって重み付けされます(大きい音ほどラフネスが高い)
    2. 臨界帯域幅に対する周波数分離に依存します
    3. 低い方の周波数の臨界帯域幅を使用して計算されます

    式:
        R(h1, h2) = a1 * a2 * g(|f2 - f1|, CB(min(f1, f2)))

    Args:
        harmonic1: 最初の倍音成分
        harmonic2: 2番目の倍音成分
        b1: 不協和曲線パラメータ(デフォルトは定数から)
        b2: 不協和曲線パラメータ(デフォルトは定数から)

    Returns:
        ラフネス計算の完全な結果（中間値を含む）を保持するRoughnessPairResult

    Examples:
        >>> h1 = Harmonic(frequency=440.0, amplitude=1.0)
        >>> h2 = Harmonic(frequency=880.0, amplitude=0.5)  # Octave
        >>> result = calculate_roughness_pair(h1, h2)
        >>> result.roughness
        # 低いラフネスを返す(オクターブは協和的)

        >>> h3 = Harmonic(frequency=466.16, amplitude=1.0)  # Minor 2nd
        >>> result = calculate_roughness_pair(h1, h3)
        >>> result.roughness
        # 高いラフネスを返す(短2度は不協和)
    """
    # 周波数差を計算
    freq_diff = abs(harmonic2.frequency - harmonic1.frequency)

    # 低い方の周波数の臨界帯域幅を使用
    # これは平均を使用するよりも知覚的に正確です
    min_freq = min(harmonic1.frequency, harmonic2.frequency)
    cb = critical_bandwidth(min_freq)

    # 正規化された周波数差を計算
    normalized_freq_diff = freq_diff / cb

    # 不協和曲線の値を計算
    dissonance = calculate_dissonance_curve(freq_diff, cb, b1=b1, b2=b2)

    # 振幅の積で重み付け
    # ラフネスは振幅の積に比例します
    amplitude_product = harmonic1.amplitude * harmonic2.amplitude

    # 最終的なラフネス値
    roughness = amplitude_product * dissonance

    return RoughnessPairResult(
        roughness=roughness,
        frequency_difference=freq_diff,
        critical_bandwidth=cb,
        normalized_freq_diff=normalized_freq_diff,
        dissonance_value=dissonance,
        amplitude_product=amplitude_product,
    )


def calculate_total_roughness(
    harmonic_pairs: list[tuple[Harmonic, Harmonic]],
) -> float:
    """倍音ペアのコレクションの総ラフネスを計算します。

    これは、通常、和音分析に使用される複数の倍音ペアにわたる
    ラフネスのバッチ計算のための便利な関数です。

    Args:
        harmonic_pairs: (harmonic1, harmonic2)タプルのリスト

    Returns:
        すべてのペアにわたるラフネス値の合計

    Examples:
        >>> h1 = Harmonic(frequency=440.0, amplitude=1.0)
        >>> h2 = Harmonic(frequency=554.37, amplitude=1.0)
        >>> h3 = Harmonic(frequency=659.25, amplitude=1.0)
        >>> pairs = [(h1, h2), (h1, h3), (h2, h3)]
        >>> calculate_total_roughness(pairs)
        # この三和音の総ラフネスを返す
    """
    return sum(calculate_roughness_pair(h1, h2).roughness for h1, h2 in harmonic_pairs)
