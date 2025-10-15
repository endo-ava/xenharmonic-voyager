"""ドメイン層と音響層を調整する協和性計算サービス。

このモジュールは、様々なチューニングシステムにおける和音の協和性スコアを
計算するための高レベルサービスを提供します。以下の調整を行います:
1. チューニングシステム(N-EDO周波数計算)
2. 倍音系列生成(音色モデル)
3. 音響的ラフネス計算(Setharesモデル)

このサービスは、調整のみに焦点を当て、ドメインロジックを適切なレイヤーに
委任することで、単一責任の原則に従います。
"""

from dataclasses import dataclass

from src.acoustics.roughness import (
    calculate_dissonance_curve,
    calculate_roughness_pair,
    critical_bandwidth,
)
from src.domain.harmonics import Harmonic, TimbreModel
from src.domain.tuning import TuningSystem
from ui.models import HarmonicPairData


@dataclass(frozen=True)
class ConsonanceResult:
    """和音の協和性計算の結果。

    Attributes:
        total_roughness: すべての倍音にわたるペアワイズラフネス値の合計。
                        値が高いほど不協和(協和性が低い)を示します。
        num_notes: 和音の音符数
        num_harmonic_pairs: 比較された倍音ペアの総数
        tuning_system: 使用されたN-EDOチューニングシステム(参照用)
        pair_details: 各倍音ペアの詳細情報（グラフ描画用）。
                     Noneの場合は詳細情報なし。
    """

    total_roughness: float
    num_notes: int
    num_harmonic_pairs: int
    tuning_system: TuningSystem
    pair_details: list[HarmonicPairData] | None = None


class ConsonanceCalculator:
    """N-EDOチューニングシステムにおける和音の協和性を計算するためのサービス。

    このサービスは、協和性計算パイプライン全体を調整します:
    1. TuningSystemを介して和音ステップを周波数にマッピング
    2. TimbreModelを介して各音符の倍音系列を生成
    3. すべての倍音の組み合わせに対してペアワイズラフネスを計算
    4. 集計された協和性メトリクスを返す

    Example:
        >>> from src.domain.tuning import TuningSystem
        >>> from src.domain.harmonics import SawtoothTimbre
        >>> calculator = ConsonanceCalculator(
        ...     tuning_system=TuningSystem(edo=12, base_frequency=440.0),
        ...     timbre_model=SawtoothTimbre(),
        ...     num_harmonics=10
        ... )
        >>> result = calculator.calculate_consonance([0, 4, 7])  # C major triad
        >>> result.total_roughness
        # 和音のラフネス値を返す
    """

    def __init__(
        self,
        tuning_system: TuningSystem,
        timbre_model: TimbreModel,
        num_harmonics: int = 10,
    ) -> None:
        """協和性計算機を初期化します。

        Args:
            tuning_system: 周波数計算のためのN-EDOチューニングシステム
            timbre_model: 倍音系列生成のための音色モデル
            num_harmonics: 各音符ごとに生成する倍音の数(デフォルト: 10)

        Raises:
            ValueError: num_harmonics < 1 の場合
        """
        if num_harmonics < 1:
            msg = f"num_harmonicsは1以上である必要がありますが、{num_harmonics}が指定されました"
            raise ValueError(msg)

        self._tuning_system = tuning_system
        self._timbre_model = timbre_model
        self._num_harmonics = num_harmonics

    def calculate_consonance(
        self, chord_steps: list[int], *, include_pair_details: bool = False
    ) -> ConsonanceResult:
        """N-EDOステップとして与えられた和音の協和性スコアを計算します。

        これは、計算全体を調整する主要な公開メソッドです。

        プロセス:
        1. 和音ステップを基本周波数に変換
        2. 各音符の倍音系列を生成
        3. すべてのペアワイズ倍音の組み合わせに対してラフネスを計算
        4. ラフネス値を合計して総不協和度を取得
        5. (オプション) グラフ描画用の詳細ペアデータを生成

        Args:
            chord_steps: 和音を表すN-EDOステップ番号のリスト。
                        例: 12-EDOの長三和音の場合は [0, 4, 7]
            include_pair_details: Trueの場合、各倍音ペアの詳細情報を含める（グラフ描画用）

        Returns:
            総ラフネスとメタデータを含むConsonanceResult

        Raises:
            ValueError: chord_stepsが空または無効なステップを含む場合

        Examples:
            >>> calculator = ConsonanceCalculator(
            ...     TuningSystem(edo=12, base_frequency=440.0),
            ...     SawtoothTimbre(),
            ...     num_harmonics=10
            ... )
            >>> result = calculator.calculate_consonance([0, 12])  # Octave
            >>> result.total_roughness < 0.1  # オクターブは協和的であるべき
            True
            >>> # グラフ用の詳細データを含める
            >>> result_with_details = calculator.calculate_consonance(
            ...     [0, 7], include_pair_details=True
            ... )
            >>> len(result_with_details.pair_details)  # ペア詳細が含まれる
            190
        """
        if not chord_steps:
            msg = "chord_stepsを空にすることはできません"
            raise ValueError(msg)

        # ステップ1:ステップを基本周波数に変換
        fundamentals = [self._tuning_system.get_frequency(step) for step in chord_steps]

        # ステップ2:各基本周波数に対して倍音系列を生成
        harmonic_series_list = [
            self._timbre_model.generate_harmonics(
                fundamental=freq, num_harmonics=self._num_harmonics
            )
            for freq in fundamentals
        ]

        # ステップ3:すべての音符からのすべての倍音をフラットなリストに収集 (メタデータ付き)
        all_harmonics_with_meta: list[tuple[int, int, Harmonic]] = []
        for note_idx, series in enumerate(harmonic_series_list):
            for harm_num, harmonic in enumerate(series.harmonics, start=1):
                all_harmonics_with_meta.append((note_idx, harm_num, harmonic))

        # ステップ4:すべてのユニークな倍音ペアに対してペアワイズラフネスを計算
        total_roughness = 0.0
        pair_details_list: list[HarmonicPairData] | None = [] if include_pair_details else None

        for i in range(len(all_harmonics_with_meta)):
            for j in range(i + 1, len(all_harmonics_with_meta)):
                note_idx1, harm_num1, harmonic1 = all_harmonics_with_meta[i]
                note_idx2, harm_num2, harmonic2 = all_harmonics_with_meta[j]

                # ラフネスを計算
                roughness = calculate_roughness_pair(harmonic1, harmonic2)
                total_roughness += roughness

                # 詳細データが必要な場合は生成
                if include_pair_details and pair_details_list is not None:
                    freq_diff = abs(harmonic2.frequency - harmonic1.frequency)
                    min_freq = min(harmonic1.frequency, harmonic2.frequency)
                    cb = critical_bandwidth(min_freq)
                    normalized_freq_diff = freq_diff / cb
                    dissonance_value = calculate_dissonance_curve(freq_diff, cb)

                    pair_data = HarmonicPairData(
                        freq1=harmonic1.frequency,
                        freq2=harmonic2.frequency,
                        amp1=harmonic1.amplitude,
                        amp2=harmonic2.amplitude,
                        normalized_freq_diff=normalized_freq_diff,
                        dissonance_value=dissonance_value,
                        roughness_contribution=roughness,
                        is_self_interference=(note_idx1 == note_idx2),
                        note_index1=note_idx1,
                        note_index2=note_idx2,
                        harmonic_number1=harm_num1,
                        harmonic_number2=harm_num2,
                    )
                    pair_details_list.append(pair_data)

        # num_pairs: C(n, 2) = n * (n - 1) / 2
        num_pairs = (len(all_harmonics_with_meta) * (len(all_harmonics_with_meta) - 1)) // 2

        return ConsonanceResult(
            total_roughness=total_roughness,
            num_notes=len(chord_steps),
            num_harmonic_pairs=num_pairs,
            tuning_system=self._tuning_system,
            pair_details=pair_details_list,
        )

    @property
    def tuning_system(self) -> TuningSystem:
        """この計算機で使用されるチューニングシステムを取得します。"""
        return self._tuning_system

    @property
    def timbre_model(self) -> TimbreModel:
        """この計算機で使用される音色モデルを取得します。"""
        return self._timbre_model

    @property
    def num_harmonics(self) -> int:
        """各音符ごとに生成される倍音の数を取得します。"""
        return self._num_harmonics
