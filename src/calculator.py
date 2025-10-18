"""協和性計算モジュール

このモジュールは、Setharesの音響的ラフネスモデルを実装し、
様々なオクターブの等分割(EDO)における和音の協和性スコアを計算します。

これは、Pydanticで検証された入力をサービスレイヤーに提供し、
単純な協和性スコアを返すAPIレイヤーです。
"""

from typing import Any

from pydantic import BaseModel, Field, field_validator

from src.constants import DEFAULT_BASE_FREQUENCY, DEFAULT_NUM_HARMONICS
from src.domain.harmonics import SawtoothTimbre
from src.domain.tuning import TuningSystem
from src.services.consonance_service import ConsonanceCalculator, ConsonanceResult


class ChordInput(BaseModel):
    """和音の協和性計算のための入力検証モデル。"""

    edo: int = Field(gt=0, description="オクターブの等分割数(N-EDO)")
    notes: list[int] = Field(
        min_length=1, description="EDOシステムにおける音符インデックスのリスト"
    )

    @field_validator("notes")
    @classmethod
    def validate_notes(cls, v: list[int], info: Any) -> list[int]:
        """すべての音符がEDOの範囲内にあることを検証します。"""
        edo = info.data.get("edo")
        if edo and any(note < 0 or note >= edo for note in v):
            msg = f"すべての音符は [0, {edo - 1}] の範囲内にある必要があります"
            raise ValueError(msg)
        return v


def calculate_consonance(
    edo: int,
    notes: list[int],
    base_frequency: float = DEFAULT_BASE_FREQUENCY,
    num_harmonics: int = DEFAULT_NUM_HARMONICS,
) -> float:
    """Setharesのラフネスモデルを使用して、和音の協和性スコアを計算します。

    これは、協和性計算のパイプラインを調整する主要なAPI関数です。
    入力を検証し、必要なコンポーネントを作成し、総音響的ラフネスを
    協和性スコアとして返します。

    注意: ラフネス値が低いほど、協和性が高い(より心地よい音)ことを示します。

    Args:
        edo: オクターブの等分割数(N-EDO)。0より大きい必要があります。
        notes: EDOシステムにおける音符ステップインデックスのリスト。空はNG。
               例: 12-EDOの長三和音の場合は [0, 4, 7]。
        base_frequency: ステップ0の基本周波数(Hz)(デフォルト: A4 = 440 Hz)
        num_harmonics: 各音符ごとに生成する倍音の数(デフォルト: 10)

    Returns:
        総音響的ラフネス(float)。値が低いほど協和的です。
        典型的な値:
        - 完全オクターブ: < 2.0
        - 長三和音: 中程度(倍音に依存)
        - 短2度: 高いラフネス

    Raises:
        ValueError: 入力検証が失敗した場合(PydanticのChordInput経由)

    Examples:
        >>> # 12-EDO 長三和音 (C-E-G)
        >>> calculate_consonance(edo=12, notes=[0, 4, 7])
        # 中程度のラフネス値を返す

        >>> # 完全オクターブ (非常に協和的)
        >>> calculate_consonance(edo=12, notes=[0, 12])
        # 低いラフネス値を返す (< 2.0)

        >>> # 19-EDO 長三度の近似
        >>> calculate_consonance(edo=19, notes=[0, 6])
        # 19-EDOの長三度のラフネスを返す
    """
    # Pydanticを使用して入力を検証
    ChordInput(edo=edo, notes=notes)

    # このEDOのためのチューニングシステムを作成
    tuning_system = TuningSystem(edo=edo, base_frequency=base_frequency)

    # 音色モデルを作成(現在はSawtoothTimbreにハードコードされています)
    timbre_model = SawtoothTimbre()

    # 協和性計算機を作成
    calculator = ConsonanceCalculator(
        tuning_system=tuning_system,
        timbre_model=timbre_model,
        num_harmonics=num_harmonics,
    )

    # 協和性を計算し、総ラフネスを返す
    result = calculator.calculate_consonance(chord_steps=notes)

    return result.total_roughness


def calculate_consonance_with_details(
    edo: int,
    notes: list[int],
    base_frequency: float = DEFAULT_BASE_FREQUENCY,
    num_harmonics: int = DEFAULT_NUM_HARMONICS,
) -> ConsonanceResult:
    """Setharesのラフネスモデルを使用して、和音の協和性スコアと詳細データを計算します。

    `calculate_consonance` と同じですが、グラフ描画用の詳細なペアデータを含む
    ConsonanceResultオブジェクトを返します。

    Args:
        edo: オクターブの等分割数(N-EDO)。0より大きい必要があります。
        notes: EDOシステムにおける音符ステップインデックスのリスト。空はNG。
               例: 12-EDOの長三和音の場合は [0, 4, 7]。
        base_frequency: ステップ0の基本周波数(Hz)(デフォルト: A4 = 440 Hz)
        num_harmonics: 各音符ごとに生成する倍音の数(デフォルト: 10)

    Returns:
        ConsonanceResult: 総ラフネス、メタデータ、グラフ用の詳細ペアデータを含む

    Raises:
        ValueError: 入力検証が失敗した場合(PydanticのChordInput経由)

    Examples:
        >>> # 詳細データ付きで計算
        >>> result = calculate_consonance_with_details(edo=12, notes=[0, 7])
        >>> result.total_roughness  # 総ラフネス
        0.0834
        >>> len(result.pair_details)  # ペア詳細データ
        190
        >>> result.pair_details[0].roughness_contribution  # 各ペアの寄与度
        0.0027
    """
    # Pydanticを使用して入力を検証
    ChordInput(edo=edo, notes=notes)

    # このEDOのためのチューニングシステムを作成
    tuning_system = TuningSystem(edo=edo, base_frequency=base_frequency)

    # 音色モデルを作成(現在はSawtoothTimbreにハードコードされています)
    timbre_model = SawtoothTimbre()

    # 協和性計算機を作成
    calculator = ConsonanceCalculator(
        tuning_system=tuning_system,
        timbre_model=timbre_model,
        num_harmonics=num_harmonics,
    )

    # 協和性を計算し、詳細データを含むConsonanceResultを返す
    return calculator.calculate_consonance(chord_steps=notes, include_pair_details=True)
