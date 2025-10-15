"""ディソナンス曲線グラフ生成モジュール

Setharesのディソナンス曲線 g(x) = exp(-b1*x) - exp(-b2*x) を可視化し、
現在の和音の倍音ペアをプロット表示します。

References:
    - Sethares, W. A. (1993). "Local consonance and the relationship between
      timbre and scale." Journal of the Acoustical Society of America, 94(3).
    - docs/70.knowledge/7004.visualization-ideas.md
"""

import numpy as np
import plotly.graph_objects as go
from plotly.graph_objects import Figure

from src.acoustics.roughness import calculate_dissonance_curve
from src.constants import ROUGHNESS_B1, ROUGHNESS_B2
from ui.models import HarmonicPairData


def generate_dissonance_curve_data(
    x_min: float = 0.0,
    x_max: float = 2.0,
    num_points: int = 500,
    b1: float = ROUGHNESS_B1,
    b2: float = ROUGHNESS_B2,
) -> tuple[np.ndarray, np.ndarray]:
    """ディソナンス曲線のデータを生成します。

    Args:
        x_min: X軸の最小値（正規化周波数差）
        x_max: X軸の最大値（正規化周波数差）
        num_points: データポイント数
        b1: ディソナンス曲線パラメータ1
        b2: ディソナンス曲線パラメータ2

    Returns:
        (x配列, g(x)配列) のタプル

    Examples:
        >>> x_vals, g_vals = generate_dissonance_curve_data()
        >>> len(x_vals), len(g_vals)
        (500, 500)
        >>> g_vals[0]  # x=0でg(x)=0
        0.0
    """
    # 正規化周波数差の範囲を生成
    x_values = np.linspace(x_min, x_max, num_points)

    # 各x値に対してディソナンス値を計算
    # CB(f) = 1.0 と仮定(正規化されているため)
    dissonance_values = np.array(
        [calculate_dissonance_curve(x, critical_band=1.0, b1=b1, b2=b2) for x in x_values]
    )

    return x_values, dissonance_values


def create_dissonance_curve_graph(
    pair_data_list: list[HarmonicPairData],
    x_min: float = 0.0,
    x_max: float = 2.0,
    show_peak_marker: bool = True,
) -> Figure:
    """ディソナンス曲線グラフを生成します。

    Args:
        pair_data_list: 倍音ペアデータのリスト（フィルタリング済みを想定）
        x_min: X軸の最小値
        x_max: X軸の最大値（表示範囲）
        show_peak_marker: ピーク位置マーカーを表示するか

    Returns:
        Plotly Figure オブジェクト

    Examples:
        >>> pairs = [...]  # calculate_consonance_with_details() の結果
        >>> fig = create_dissonance_curve_graph(pairs)
        >>> fig.show()
    """

    # ディソナンス曲線のデータ生成
    x_curve, g_curve = generate_dissonance_curve_data(x_min=x_min, x_max=x_max)

    # Figureの作成
    fig = go.Figure()

    # タイトル用の統計情報
    total_count = len(pair_data_list)

    # 1. ディソナンス曲線本体
    fig.add_trace(
        go.Scatter(
            x=x_curve,
            y=g_curve,
            mode="lines",
            name="Dissonance Curve g(x)",
            line={"color": "gray", "width": 2},
            hovertemplate="x: %{x:.3f}<br>g(x): %{y:.4f}<extra></extra>",
        )
    )

    # 2. ピーク位置の縦線(x ≈ 0.24)
    if show_peak_marker:
        # ピーク位置の理論値
        peak_x = np.log(ROUGHNESS_B2 / ROUGHNESS_B1) / (ROUGHNESS_B2 - ROUGHNESS_B1)
        peak_g = calculate_dissonance_curve(peak_x, critical_band=1.0)

        fig.add_trace(
            go.Scatter(
                x=[peak_x, peak_x],
                y=[0, peak_g],
                mode="lines",
                name="Peak Position",
                line={"color": "orange", "width": 1, "dash": "dash"},
                hovertemplate=f"Peak at x ≈ {peak_x:.3f}<extra></extra>",
            )
        )

        # ピーク位置に注釈を追加
        fig.add_annotation(
            x=peak_x,
            y=peak_g,
            text=f"Max Dissonance<br>x ≈ {peak_x:.2f}",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=1,
            arrowcolor="orange",
            ax=40,
            ay=-40,
            bgcolor="rgba(255, 255, 255, 0.8)",
            bordercolor="orange",
            borderwidth=1,
        )

    # 3. 倍音ペアのプロット(自己干渉と相互干渉で色分け)
    if pair_data_list:
        # 自己干渉(同一音内)
        self_pairs = [p for p in pair_data_list if p.is_self_interference]
        if self_pairs:
            self_x = [p.normalized_freq_diff for p in self_pairs]
            self_y = [p.dissonance_value for p in self_pairs]
            self_hover_text = [
                f"<b>Self-Interference</b><br>"
                f"Note {p.note_index1}: H{p.harmonic_number1} ↔ H{p.harmonic_number2}<br>"
                f"Freq: {p.freq1:.1f} Hz ↔ {p.freq2:.1f} Hz<br>"
                f"Normalized Δf (x): {p.normalized_freq_diff:.3f}<br>"
                f"Dissonance g(x): {p.dissonance_value:.4f}<br>"
                f"Roughness Contribution: {p.roughness_contribution:.6f}"
                for p in self_pairs
            ]

            fig.add_trace(
                go.Scatter(
                    x=self_x,
                    y=self_y,
                    mode="markers",
                    name="Self-Interference (同一音内)",
                    marker={
                        "color": "blue",
                        "size": 6,
                        "opacity": 0.6,
                        "line": {"width": 0.5, "color": "darkblue"},
                    },
                    text=self_hover_text,
                    hovertemplate="%{text}<extra></extra>",
                )
            )

        # 相互干渉(異なる音間)
        mutual_pairs = [p for p in pair_data_list if not p.is_self_interference]
        if mutual_pairs:
            mutual_x = [p.normalized_freq_diff for p in mutual_pairs]
            mutual_y = [p.dissonance_value for p in mutual_pairs]
            mutual_hover_text = [
                f"<b>Mutual-Interference</b><br>"
                f"Note {p.note_index1}-H{p.harmonic_number1} ↔ "
                f"Note {p.note_index2}-H{p.harmonic_number2}<br>"
                f"Freq: {p.freq1:.1f} Hz ↔ {p.freq2:.1f} Hz<br>"
                f"Normalized Δf (x): {p.normalized_freq_diff:.3f}<br>"
                f"Dissonance g(x): {p.dissonance_value:.4f}<br>"
                f"Roughness Contribution: {p.roughness_contribution:.6f}"
                for p in mutual_pairs
            ]

            fig.add_trace(
                go.Scatter(
                    x=mutual_x,
                    y=mutual_y,
                    mode="markers",
                    name="Mutual-Interference (異なる音間)",
                    marker={
                        "color": "red",
                        "size": 6,
                        "opacity": 0.6,
                        "line": {"width": 0.5, "color": "darkred"},
                    },
                    text=mutual_hover_text,
                    hovertemplate="%{text}<extra></extra>",
                )
            )

    # レイアウト設定
    fig.update_layout(
        title=f"Dissonance Curve with Harmonic Pairs ({total_count} pairs)",
        xaxis_title="Normalized Frequency Difference (x = Δf / CB)",
        yaxis_title="Dissonance g(x)",
        hovermode="closest",
        showlegend=True,
        legend={"x": 0.7, "y": 0.98, "bgcolor": "rgba(255, 255, 255, 0.8)"},
        plot_bgcolor="white",
        xaxis={
            "gridcolor": "lightgray",
            "showgrid": True,
            "zeroline": True,
            "zerolinewidth": 1,
            "zerolinecolor": "black",
        },
        yaxis={
            "gridcolor": "lightgray",
            "showgrid": True,
            "zeroline": True,
            "zerolinewidth": 1,
            "zerolinecolor": "black",
        },
        height=500,
    )

    return fig
