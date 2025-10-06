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

from src.acoustics.roughness import calculate_roughness_pair
from src.domain.harmonics import Harmonic, TimbreModel
from src.domain.tuning import TuningSystem


@dataclass(frozen=True)
class ConsonanceResult:
    """和音の協和性計算の結果。

    Attributes:
        total_roughness: すべての倍音にわたるペアワイズラフネス値の合計。
                        値が高いほど不協和(協和性が低い)を示します。
        num_notes: 和音の音符数
        num_harmonic_pairs: 比較された倍音ペアの総数
        tuning_system: 使用されたN-EDOチューニングシステム(参照用)
    """

    total_roughness: float
    num_notes: int
    num_harmonic_pairs: int
    tuning_system: TuningSystem


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

    def calculate_consonance(self, chord_steps: list[int]) -> ConsonanceResult:
        """N-EDOステップとして与えられた和音の協和性スコアを計算します。

        これは、計算全体を調整する主要な公開メソッドです。

        プロセス:
        1. 和音ステップを基本周波数に変換
        2. 各音符の倍音系列を生成
        3. すべてのペアワイズ倍音の組み合わせに対してラフネスを計算
        4. ラフネス値を合計して総不協和度を取得

        Args:
            chord_steps: 和音を表すN-EDOステップ番号のリスト。
                        例: 12-EDOの長三和音の場合は [0, 4, 7]

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

        # ステップ3:すべての音符からのすべての倍音をフラットなリストに収集
        all_harmonics: list[Harmonic] = []
        for series in harmonic_series_list:
            all_harmonics.extend(series.harmonics)

        # ステップ4:すべてのユニークな倍音ペアに対してペアワイズラフネスを計算
        total_roughness = 0.0
        num_pairs = 0

        # ネストしたループを使用してすべてのユニークなペアを取得(i < j)
        for i in range(len(all_harmonics)):
            for j in range(i + 1, len(all_harmonics)):
                roughness = calculate_roughness_pair(all_harmonics[i], all_harmonics[j])
                total_roughness += roughness
                num_pairs += 1

        return ConsonanceResult(
            total_roughness=total_roughness,
            num_notes=len(chord_steps),
            num_harmonic_pairs=num_pairs,
            tuning_system=self._tuning_system,
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
