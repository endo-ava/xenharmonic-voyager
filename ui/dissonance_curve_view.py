"""ディソナンス曲線表示UIコンポーネント (View層)

このモジュールは、DissonanceCurveViewModelを受け取り、Streamlitで描画のみを行います。
ビジネスロジックは src/visualization/dissonance_curve.py に配置されています。
"""

import streamlit as st

from src.visualization.dissonance_curve import DissonanceCurveViewModel


def render_dissonance_curve_view(
    view_model: DissonanceCurveViewModel | None,
) -> None:
    """ディソナンス曲線グラフを描画します。

    Args:
        view_model: Presenter層で準備されたDissonanceCurveViewModel
    """
    if not view_model:
        st.info("データが不足しています。")
        return

    # Streamlitでグラフを表示
    st.plotly_chart(view_model.fig, use_container_width=True)

    # 統計情報の表示
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Pairs (All)", view_model.total_pairs, help="全倍音ペア数")
    with col2:
        st.metric(
            "Displayed Pairs",
            view_model.displayed_pairs,
            delta=f"-{view_model.total_pairs - view_model.displayed_pairs}",
            help="フィルタリング後の表示ペア数",
        )
    with col3:
        st.metric(
            "Self (Displayed)",
            view_model.self_interference_filtered,
            delta=f"/ {view_model.self_interference_all}",
            help="表示中の自己干渉ペア数",
        )
    with col4:
        st.metric(
            "Mutual (Displayed)",
            view_model.mutual_interference_filtered,
            delta=f"/ {view_model.mutual_interference_all}",
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
