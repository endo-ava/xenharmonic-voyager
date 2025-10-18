"""ドメイン層のプロトコル定義。

このモジュールは、依存性逆転の原則(DIP)を実現するための
抽象インターフェース(Protocol)を定義します。
"""

from typing import Protocol

from src.domain.constants import DEFAULT_NUM_HARMONICS
from src.domain.models import HarmonicSeries


class TimbreModel(Protocol):
    """倍音系列を生成する音色モデルのプロトコル。

    音色モデルは、特定の音質(ノコギリ波、矩形波など)に対する
    倍音間の振幅分布を定義します。

    このProtocolにより、ConsonanceCalculatorは具体的な音色実装に
    依存せず、抽象的なTimbreModelに依存することができます。
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
