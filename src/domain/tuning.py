"""N-EDO(オクターブの等分割)のためのチューニングシステムモデル。

このモジュールは、様々な等分律チューニングシステムにおける周波数を
表現し計算するための中心的なドメインモデルを提供します。
"""

from dataclasses import dataclass

import numpy as np

from src.constants import DEFAULT_BASE_FREQUENCY


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
