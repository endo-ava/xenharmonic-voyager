"""ディソナンス曲線表示UIコンポーネント"""

import streamlit as st

from src.visualization.dissonance_curve import (
    HarmonicPairData,
    create_dissonance_curve_graph,
)


def render_dissonance_curve_view(
    pair_details: list[HarmonicPairData] | None,
) -> None:
    """ディソナンス曲線グラフを表示します。

    Args:
        pair_details: 事前計算された倍音ペア詳細データ
                     (calculate_consonance_with_details から取得)
    """
    if not pair_details:
        st.info("データが不足しています。")
        return

    # フィルタリング前の統計 (全ペアデータ)
    total_pairs = len(pair_details)
    self_interference_all = sum(1 for p in pair_details if p.is_self_interference)
    mutual_interference_all = total_pairs - self_interference_all

    # フィルタリング実行
    total_roughness = sum(p.roughness_contribution for p in pair_details)
    min_threshold = total_roughness * 0.001  # 0.1%閾値
    filtered_pairs = [p for p in pair_details if p.roughness_contribution >= min_threshold]

    # グラフの生成 (フィルタ済みデータを渡す)
    fig = create_dissonance_curve_graph(filtered_pairs)

    # Streamlitでグラフを表示
    st.plotly_chart(fig, use_container_width=True)

    # フィルタリング後の統計
    self_interference_filtered = sum(1 for p in filtered_pairs if p.is_self_interference)
    mutual_interference_filtered = len(filtered_pairs) - self_interference_filtered

    # 統計情報の表示
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Pairs (All)", total_pairs, help="全倍音ペア数")
    with col2:
        st.metric(
            "Displayed Pairs",
            len(filtered_pairs),
            delta=f"-{total_pairs - len(filtered_pairs)}",
            help="フィルタリング後の表示ペア数",
        )
    with col3:
        st.metric(
            "Self (Displayed)",
            self_interference_filtered,
            delta=f"/ {self_interference_all}",
            help="表示中の自己干渉ペア数",
        )
    with col4:
        st.metric(
            "Mutual (Displayed)",
            mutual_interference_filtered,
            delta=f"/ {mutual_interference_all}",
            help="表示中の相互干渉ペア数",
        )

    # 解説
    st.markdown(
        """
        **グラフの見方:**
        倍音ペアがディソナンス曲線のピーク近傍に集中している場合、
        その和音は不協和的 (ラフネスが高い) になります。
        逆に、ピークから離れた位置にある場合は協和的です。

        - **灰色の曲線**: Setharesのディソナンス曲線 g(x)
        - **オレンジの破線**: 最大ディソナンス位置 (x ≈ 0.24)
        - **青い点**: 同一音内の倍音ペア (自己干渉)
        - **赤い点**: 異なる音間の倍音ペア (相互干渉)

        **表示の最適化:**
        - ラフネス寄与度が総ラフネスの0.1%未満のペアは非表示にしています
        - これにより、聴覚的に重要なペアだけを見やすく表示しています

        各点にカーソルを合わせると、詳細な情報が表示されます。
        """
    )
