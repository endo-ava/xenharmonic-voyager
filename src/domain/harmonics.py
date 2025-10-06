"""音色表現のための倍音系列モデル。

このモジュールは、協和性計算で使用される倍音系列と音色モデルを
表現するためのモデルを定義します。
"""

from dataclasses import dataclass
from typing import Protocol

import numpy as np

from src.constants import DEFAULT_NUM_HARMONICS


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


class TimbreModel(Protocol):
    """倍音系列を生成する音色モデルのプロトコル。

    音色モデルは、特定の音質(ノコギリ波、矩形波など)に対する
    倍音間の振幅分布を定義します。
    """

    def generate_harmonics(
        self, fundamental: float, num_harmonics: int = DEFAULT_NUM_HARMONICS
    ) -> HarmonicSeries:
        """指定された基本周波数の倍音系列を生成します。

        Args:
            fundamental: 基本周波数(Hz)
            num_harmonics: 生成する倍音の数(デフォルト: 10)

        Returns:
            倍音を含むHarmonicSeriesオブジェクト
        """
        ...


class SawtoothTimbre:
    """1/kの振幅減衰を持つノコギリ波/音色モデル。

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
