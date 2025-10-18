"""Visualization layer data models.

このモジュールは、可視化層で使用されるデータモデルを定義します。
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class HarmonicPairData:
    """倍音ペアの情報を格納するデータクラス

    Attributes:
        freq1: 第1倍音の周波数 (Hz)
        freq2: 第2倍音の周波数 (Hz)
        amp1: 第1倍音の振幅
        amp2: 第2倍音の振幅
        normalized_freq_diff: 正規化周波数差 x = Δf / CB(f_min)
        dissonance_value: ディソナンス値 g(x)
        roughness_contribution: ラフネス寄与度 R = a1 × a2 × g(x)
        is_self_interference: 同一音内の倍音ペアかどうか
        note_index1: 第1音の音番号（0始まり）
        note_index2: 第2音の音番号（0始まり）
        harmonic_number1: 第1倍音の次数
        harmonic_number2: 第2倍音の次数
    """

    freq1: float
    freq2: float
    amp1: float
    amp2: float
    normalized_freq_diff: float
    dissonance_value: float
    roughness_contribution: float
    is_self_interference: bool
    note_index1: int
    note_index2: int
    harmonic_number1: int
    harmonic_number2: int
