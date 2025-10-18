"""アプリケーション層のユースケース。

このモジュールは、協和性計算のビジネスロジックを調整する
Use Caseクラスを定義します。
"""

from src.application.dto import ChordInput
from src.domain.constants import DEFAULT_BASE_FREQUENCY, DEFAULT_NUM_HARMONICS
from src.domain.models import SawtoothTimbre, TuningSystem
from src.domain.services import ConsonanceCalculator, ConsonanceResult


class CalculateConsonanceUseCase:
    """和音の協和性を計算するUse Case。

    このクラスは、協和性計算のパイプライン全体を調整します:
    1. 入力を検証 (ChordInput)
    2. 必要なドメインオブジェクトを作成 (TuningSystem, TimbreModel)
    3. Domain Serviceを実行 (ConsonanceCalculator)
    4. 結果を返す (ConsonanceResult)

    このUse Caseは、UI層とDomain層の橋渡しを担当し、
    依存性の注入とオーケストレーションを提供します。

    Examples:
        >>> use_case = CalculateConsonanceUseCase()
        >>> # 12-EDO 長三和音 (C-E-G)
        >>> result = use_case.execute(
        ...     edo=12,
        ...     notes=[0, 4, 7],
        ...     num_harmonics=10,
        ...     include_pair_details=False
        ... )
        >>> result.total_roughness
        # 中程度のラフネス値を返す

        >>> # 詳細データ付きで計算
        >>> result_with_details = use_case.execute(
        ...     edo=12,
        ...     notes=[0, 7],
        ...     num_harmonics=10,
        ...     include_pair_details=True
        ... )
        >>> len(result_with_details.pair_details)
        190
    """

    def execute(
        self,
        edo: int,
        notes: list[int],
        base_frequency: float = DEFAULT_BASE_FREQUENCY,
        num_harmonics: int = DEFAULT_NUM_HARMONICS,
        *,
        include_pair_details: bool = False,
    ) -> ConsonanceResult:
        """協和性計算を実行します。

        Args:
            edo: オクターブの等分割数(N-EDO)。0より大きい必要があります。
            notes: EDOシステムにおける音符ステップインデックスのリスト。空はNG。
                   例: 12-EDOの長三和音の場合は [0, 4, 7]。
            base_frequency: ステップ0の基本周波数(Hz)(デフォルト: A4 = 440 Hz)
            num_harmonics: 各音符ごとに生成する倍音の数(デフォルト: 10)
            include_pair_details: Trueの場合、グラフ描画用の詳細ペアデータを含める

        Returns:
            ConsonanceResult: 総ラフネス、メタデータ、オプションで詳細ペアデータを含む

        Raises:
            ValueError: 入力検証が失敗した場合(PydanticのChordInput経由)

        Examples:
            >>> use_case = CalculateConsonanceUseCase()
            >>> # 簡易計算 (詳細データなし)
            >>> result = use_case.execute(edo=12, notes=[0, 12])
            >>> result.total_roughness  # 総ラフネス
            # < 2.0 (オクターブは協和的)

            >>> # 詳細計算 (ペアデータ付き)
            >>> result = use_case.execute(
            ...     edo=12, notes=[0, 4, 7], include_pair_details=True
            ... )
            >>> result.pair_details[0].roughness_contribution
            # 各ペアの寄与度
        """
        # ステップ1: Pydanticを使用して入力を検証
        ChordInput(edo=edo, notes=notes)

        # ステップ2: このEDOのためのチューニングシステムを作成
        tuning_system = TuningSystem(edo=edo, base_frequency=base_frequency)

        # ステップ3: 音色モデルを作成(現在はSawtoothTimbreにハードコードされています)
        timbre_model = SawtoothTimbre()

        # ステップ4: 協和性計算機を作成
        calculator = ConsonanceCalculator(
            tuning_system=tuning_system,
            timbre_model=timbre_model,
            num_harmonics=num_harmonics,
        )

        # ステップ5: 協和性を計算し、ConsonanceResultを返す
        return calculator.calculate_consonance(
            chord_steps=notes, include_pair_details=include_pair_details
        )
