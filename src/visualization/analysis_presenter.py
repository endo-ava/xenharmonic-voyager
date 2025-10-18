"""Analysis view用のPresenter層

このモジュールは、ラフネス解析結果をUI表示用に準備します。
ビジネスロジックと描画ロジックを分離するため、ViewModelパターンを採用しています。
"""

from dataclasses import dataclass

from config.constants import MAX_ROUGHNESS_FOR_PROGRESS, RoughnessLevel


@dataclass(frozen=True)
class AnalysisViewModel:
    """ラフネス解析結果の表示用データモデル

    Attributes:
        roughness: 計算されたラフネス値
        roughness_level: 協和度レベルのラベル文字列
        inverted_progress: プログレスバー用の反転された値 (0.0-1.0)
    """

    roughness: float
    roughness_level: str
    inverted_progress: float


def get_roughness_level(roughness: float) -> str:
    """ラフネス値から協和度レベルを取得します。

    Args:
        roughness: 分類するラフネス値

    Returns:
        str: 協和度レベルのラベル

    Examples:
        >>> get_roughness_level(0.3)
        'L1 (Very Consonant)'
        >>> get_roughness_level(5.0)
        'L5 (Dissonant)'
    """
    levels = [
        (RoughnessLevel.VERY_CONSONANT, "L1 (Very Consonant)"),
        (RoughnessLevel.CONSONANT, "L2 (Consonant)"),
        (RoughnessLevel.SLIGHTLY_CONSONANT, "L3 (Slightly Consonant)"),
        (RoughnessLevel.SLIGHTLY_DISSONANT, "L4 (Slightly Dissonant)"),
    ]
    return next(
        (label for threshold, label in levels if roughness < threshold),
        "L5 (Dissonant)",
    )


def calculate_inverted_progress(
    roughness: float,
    max_roughness: float = MAX_ROUGHNESS_FOR_PROGRESS,
) -> float:
    """ラフネス値を反転プログレスバー値に変換します。

    値が小さいほど長いバーになるように反転します。

    Args:
        roughness: ラフネス値
        max_roughness: プログレス計算用の最大ラフネス値

    Returns:
        float: 0.0から1.0の範囲のプログレス値

    Examples:
        >>> calculate_inverted_progress(0.0)
        1.0
        >>> calculate_inverted_progress(2.0, max_roughness=2.0)
        0.0
        >>> calculate_inverted_progress(1.0, max_roughness=2.0)
        0.5
    """
    return max(0.0, min(1.0, (max_roughness - roughness) / max_roughness))


def prepare_analysis_view_model(roughness: float) -> AnalysisViewModel:
    """ラフネス値からAnalysisViewModelを準備します。

    Args:
        roughness: 計算されたラフネス値

    Returns:
        AnalysisViewModel: UI表示用の準備されたデータモデル

    Examples:
        >>> vm = prepare_analysis_view_model(0.5)
        >>> vm.roughness
        0.5
        >>> vm.roughness_level
        'L2 (Consonant)'
        >>> 0.0 <= vm.inverted_progress <= 1.0
        True
    """
    return AnalysisViewModel(
        roughness=roughness,
        roughness_level=get_roughness_level(roughness),
        inverted_progress=calculate_inverted_progress(roughness),
    )
