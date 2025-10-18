"""アプリケーション層のDTO (Data Transfer Object)。

このモジュールは、アプリケーション層での入力検証とデータ転送のための
DTOモデルを定義します。
"""

from typing import Any

from pydantic import BaseModel, Field, field_validator


class ChordInput(BaseModel):
    """和音の協和性計算のための入力検証モデル。

    Pydanticを使用して、UI層からの入力を検証します。

    Attributes:
        edo: オクターブの等分割数(N-EDO)。正の整数である必要があります。
        notes: EDOシステムにおける音符インデックスのリスト。
               空でないリストで、各要素は [0, edo-1] の範囲内である必要があります。

    Examples:
        >>> # 12-EDO 長三和音 (C-E-G)
        >>> chord = ChordInput(edo=12, notes=[0, 4, 7])
        >>> chord.edo
        12
        >>> chord.notes
        [0, 4, 7]

        >>> # 19-EDO 長三度の近似
        >>> chord = ChordInput(edo=19, notes=[0, 6])
        >>> chord.edo
        19

        >>> # 無効な入力: edo範囲外の音符
        >>> ChordInput(edo=12, notes=[0, 15])
        # ValueError: すべての音符は [0, 11] の範囲内にある必要があります
    """

    edo: int = Field(gt=0, description="オクターブの等分割数(N-EDO)")
    notes: list[int] = Field(
        min_length=1, description="EDOシステムにおける音符インデックスのリスト"
    )

    @field_validator("notes")
    @classmethod
    def validate_notes(cls, v: list[int], info: Any) -> list[int]:
        """すべての音符がEDOの範囲内にあることを検証します。

        Args:
            v: 検証対象の音符リスト
            info: Pydanticから提供される検証コンテキスト情報

        Returns:
            検証済みの音符リスト

        Raises:
            ValueError: 音符がEDOの範囲外の場合
        """
        edo = info.data.get("edo")
        if edo and any(note < 0 or note >= edo for note in v):
            msg = f"すべての音符は [0, {edo - 1}] の範囲内にある必要があります"
            raise ValueError(msg)
        return v
