"""ドメイン層のモデル定義。

このモジュールは、協和性計算で使用される中心的なドメインモデルを定義します:
- TuningSystem: N-EDOチューニングシステム
- Harmonic: 単一の倍音成分
- HarmonicSeries: 倍音系列
- SawtoothTimbre: ノコギリ波音色モデル
- RoughnessPairResult: ラフネス計算結果
"""

from dataclasses import dataclass

import numpy as np

from src.domain.constants import DEFAULT_BASE_FREQUENCY, DEFAULT_NUM_HARMONICS


@dataclass(frozen=True)
class TuningSystem:
    """N-EDO(オクターブの等分割)チューニングシステム。

    このクラスは、オクターブがN個の等しいステップに分割される等分律
    チューニングシステムを表します。特定音度の周波数を計算するメソッドを提供します。

    Mathematical Foundation:
        基本周波数f₀を持つN-EDOシステムの場合:
        f(n) = f₀ * 2^(n/N)

        ここで、nはステップインデックス(0 ≤ n < N)です。

    Attributes:
        edo: オクターブの等分割数(例:12-TETの場合は12、19-EDOの場合は19)
        base_frequency: 基準周波数(Hz)(デフォルト:440.0 Hz = A4)

    Examples:
        >>> # 12-EDO(標準的な12音等分律)
        >>> tuning_12 = TuningSystem(edo=12, base_frequency=440.0)
        >>> tuning_12.get_frequency(0)   # A4
        440.0
        >>> tuning_12.get_frequency(12)  # A5(1オクターブ上)
        880.0

        >>> # 19-EDO(拡張等分律)
        >>> tuning_19 = TuningSystem(edo=19)
        >>> tuning_19.get_frequency(0)
        440.0
    """

    edo: int
    base_frequency: float = DEFAULT_BASE_FREQUENCY

    def __post_init__(self) -> None:
        """チューニングシステムのパラメータを検証します。

        Raises:
            ValueError: edo <= 0 または base_frequency <= 0 の場合
        """
        if self.edo <= 0:
            msg = f"EDOは正である必要がありますが、{self.edo}が指定されました"
            raise ValueError(msg)
        if self.base_frequency <= 0:
            msg = f"基本周波数は正である必要がありますが、{self.base_frequency}が指定されました"
            raise ValueError(msg)

    def get_frequency(self, step: int) -> float:
        """EDOシステムにおける指定されたステップの周波数を計算します。

        指数関数式を使用します: f(n) = f₀ * 2^(n/N)

        Args:
            step: EDOシステムのステップインデックス。任意の整数が可能です:
                - 0は基本周波数を返します
                - Nは基本周波数の1オクターブ上を返します
                - 負の値はより低いオクターブを返します
                - N以上の値はより高いオクターブを返します

        Returns:
            指定されたステップに対応する周波数(Hz)

        Examples:
            >>> tuning = TuningSystem(edo=12, base_frequency=440.0)
            >>> tuning.get_frequency(0)   # A4
            440.0
            >>> tuning.get_frequency(7)   # E5 (perfect fifth)
            659.2551138257401
            >>> tuning.get_frequency(12)  # A5 (octave)
            880.0
            >>> tuning.get_frequency(-12) # A3 (octave down)
            220.0
        """
        return float(self.base_frequency * (2.0 ** (step / self.edo)))

    def get_interval_cents(self, steps: int) -> float:
        """指定されたステップ数のインターバルサイズをセントで計算します。

        1セントは12-EDOにおける半音の1/100です。これにより、
        異なるオクターブ間で一貫した対数的なインターバルサイズの尺度が提供されます。

        Formula: cents = 1200 * log₂(f₂/f₁) = 1200 * (steps/N)

        Args:
            steps: EDOシステムにおけるステップ数

        Returns:
            インターバルサイズ(セント)

        Examples:
            >>> tuning = TuningSystem(edo=12)
            >>> tuning.get_interval_cents(1)   # 12-EDOの半音
            100.0
            >>> tuning.get_interval_cents(12)  # オクターブ
            1200.0

            >>> tuning_19 = TuningSystem(edo=19)
            >>> tuning_19.get_interval_cents(1)  # 19-EDOのステップ
            63.15789473684211
        """
        return 1200.0 * steps / self.edo

    def get_frequencies_for_chord(self, steps: list[int]) -> np.ndarray:
        """複数のステップ(和音の音符)の周波数を計算します。

        これは、NumPyのベクトル化で最適化された、複数の周波数を
        バッチ計算するための便利なメソッドです。

        Args:
            steps: ステップインデックスのリスト

        Returns:
            入力ステップと同じ順序の周波数のNumPy配列(Hz)

        Examples:
            >>> tuning = TuningSystem(edo=12, base_frequency=440.0)
            >>> tuning.get_frequencies_for_chord([0, 4, 7])  # Major triad
            array([440.        , 554.36526195, 659.25511383])
        """
        steps_array = np.array(steps, dtype=np.float64)
        return self.base_frequency * np.power(2.0, steps_array / self.edo)

    def __repr__(self) -> str:
        """チューニングシステムの文字列表現を返します。"""
        return f"TuningSystem(edo={self.edo}, base_frequency={self.base_frequency:.2f} Hz)"


@dataclass(frozen=True)
class Harmonic:
    """周波数と振幅を持つ単一の倍音成分。

    Attributes:
        frequency: 周波数(Hz)
        amplitude: 振幅([0.0, 1.0]の範囲)
    """

    frequency: float
    amplitude: float

    def __post_init__(self) -> None:
        """倍音パラメータを検証します。"""
        if self.frequency <= 0:
            msg = f"周波数は正である必要がありますが、{self.frequency}が指定されました"
            raise ValueError(msg)
        if not 0.0 <= self.amplitude <= 1.0:
            msg = f"振幅は[0, 1]の範囲内である必要がありますが、{self.amplitude}が指定されました"
            raise ValueError(msg)


@dataclass(frozen=True)
class HarmonicSeries:
    """音色を形成する倍音成分のコレクション。

    Attributes:
        harmonics: Harmonicオブジェクトのタプル(倍音番号順)
    """

    harmonics: tuple[Harmonic, ...]

    def __post_init__(self) -> None:
        """倍音系列を検証します。"""
        if len(self.harmonics) == 0:
            msg = "HarmonicSeriesには少なくとも1つの倍音が含まれている必要があります"
            raise ValueError(msg)

    def get_frequencies(self) -> np.ndarray:
        """すべての倍音周波数の配列を取得します。

        Returns:
            周波数のNumPy配列(Hz)
        """
        return np.array([h.frequency for h in self.harmonics], dtype=np.float64)

    def get_amplitudes(self) -> np.ndarray:
        """すべての倍音振幅の配列を取得します。

        Returns:
            振幅のNumPy配列
        """
        return np.array([h.amplitude for h in self.harmonics], dtype=np.float64)

    def __len__(self) -> int:
        """系列内の倍音の数を返します。"""
        return len(self.harmonics)

    def __repr__(self) -> str:
        """文字列表現を返します。"""
        return f"HarmonicSeries(num_harmonics={len(self)})"


class SawtoothTimbre:
    """1/kの振幅減衰を持つノコギリ波音色モデル。

    この音色モデルは、k番目の倍音が1/kに比例する振幅を持つ
    ノコギリ波スペクトルに従います。

    Mathematical Model:
        k番目の倍音(k = 1, 2, 3, ...)について:
        - frequency_k = k * f₀
        - amplitude_k = 1/k

    これにより、ノコギリ波に特徴的な豊かで明るい音色が生まれます。

    Examples:
        >>> timbre = SawtoothTimbre()
        >>> series = timbre.generate_harmonics(440.0, num_harmonics=3)
        >>> len(series)
        3
        >>> series.harmonics[0].amplitude  # 1番目の倍音
        1.0
        >>> series.harmonics[1].amplitude  # 2番目の倍音
        0.5
        >>> series.harmonics[2].amplitude  # 3番目の倍音
        0.3333333333333333
    """

    def generate_harmonics(
        self, fundamental: float, num_harmonics: int = DEFAULT_NUM_HARMONICS
    ) -> HarmonicSeries:
        """ノコギリ波の倍音系列を生成します。

        Args:
            fundamental: 基本周波数(Hz)(正である必要があります)
            num_harmonics: 生成する倍音の数(1以上である必要があります)

        Returns:
            1/kの振幅減衰を持つHarmonicSeries

        Raises:
            ValueError: fundamental <= 0 または num_harmonics < 1 の場合

        Examples:
            >>> timbre = SawtoothTimbre()
            >>> series = timbre.generate_harmonics(440.0, num_harmonics=10)
            >>> len(series)
            10
            >>> series.harmonics[0].frequency  # 1番目の倍音
            440.0
            >>> series.harmonics[1].frequency  # 2番目の倍音
            880.0
        """
        if fundamental <= 0:
            msg = f"基本周波数は正である必要がありますが、{fundamental}が指定されました"
            raise ValueError(msg)
        if num_harmonics < 1:
            msg = f"倍音の数は1以上である必要がありますが、{num_harmonics}が指定されました"
            raise ValueError(msg)

        # 倍音番号を生成: 1, 2, 3, ..., num_harmonics
        harmonic_numbers = np.arange(1, num_harmonics + 1, dtype=np.float64)

        # 周波数を計算: k * f₀
        frequencies = fundamental * harmonic_numbers

        # 振幅を計算: 1/k
        amplitudes = 1.0 / harmonic_numbers

        # Harmonicオブジェクトを作成
        harmonics = tuple(
            Harmonic(frequency=freq, amplitude=amp)
            for freq, amp in zip(frequencies, amplitudes, strict=True)
        )

        return HarmonicSeries(harmonics=harmonics)

    def __repr__(self) -> str:
        """文字列表現を返します。"""
        return "SawtoothTimbre(decay=1/k)"


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
