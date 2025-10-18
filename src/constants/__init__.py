"""定数モジュール - ドメインロジックとUI表示用の定数。

このモジュールは、プロジェクト全体で使用される定数を提供します。
定数は責務ごとに分離されています:
- domain: ドメインロジック（音響計算、チューニングシステム）
- ui: UI表示（Streamlitアプリケーション）
"""

# ドメイン定数の再エクスポート (新しい場所から)
# UI定数の再エクスポート
from src.constants.ui import (
    ROUGHNESS_CONSONANT,
    ROUGHNESS_EXTREMELY_CONSONANT,
    ROUGHNESS_SLIGHTLY_CONSONANT,
    ROUGHNESS_SLIGHTLY_DISSONANT,
)
from src.domain.constants import (
    CB_COEFFICIENT,
    CB_CONSTANT,
    DEFAULT_BASE_FREQUENCY,
    DEFAULT_NUM_HARMONICS,
    REFERENCE_CHORD_12EDO_MAJOR,
    REFERENCE_FREQUENCY,
    ROUGHNESS_B1,
    ROUGHNESS_B2,
    SUPPORTED_EDO_SYSTEMS,
)

__all__ = [
    # Domain constants
    "CB_COEFFICIENT",
    "CB_CONSTANT",
    "DEFAULT_BASE_FREQUENCY",
    "DEFAULT_NUM_HARMONICS",
    "REFERENCE_CHORD_12EDO_MAJOR",
    "REFERENCE_FREQUENCY",
    "ROUGHNESS_B1",
    "ROUGHNESS_B2",
    # UI constants
    "ROUGHNESS_CONSONANT",
    "ROUGHNESS_EXTREMELY_CONSONANT",
    "ROUGHNESS_SLIGHTLY_CONSONANT",
    "ROUGHNESS_SLIGHTLY_DISSONANT",
    "SUPPORTED_EDO_SYSTEMS",
]
