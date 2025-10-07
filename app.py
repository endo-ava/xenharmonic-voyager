"""Xenharmonic Voyager - メインStreamlitアプリケーション

このモジュールは、Setharesの音響的ラフネスモデルを使用して、
異種調和の協和性を探求するためのユーザーインターフェースを提供します。
"""

import streamlit as st
from pydantic import ValidationError

from src.calculator import calculate_consonance
from src.constants import (
    ROUGHNESS_CONSONANT,
    ROUGHNESS_EXTREMELY_CONSONANT,
    ROUGHNESS_SLIGHTLY_CONSONANT,
    ROUGHNESS_SLIGHTLY_DISSONANT,
)

st.set_page_config(
    page_title="Xenharmonic Voyager",
    page_icon="🎵",
    layout="wide",
)

# タイトルと説明
st.title("Xenharmonic Voyager")
st.markdown(
    """
**Setharesの音響的ラフネスモデル**を使用して、さまざまなチューニングシステムにおける
協和性を探求します。ラフネス値が低いほど、協和性が高い(より心地よい音)ことを示します。
"""
)

# 設定用サイドバー
with st.sidebar:
    st.header("設定")

    edo = st.number_input(
        "EDO (Equal Divisions of Octave)",
        min_value=1,
        max_value=100,
        value=12,
        help="1オクターブあたりの等しい分割数。12-EDO = 標準的な西洋音律。",
    )

    base_frequency = st.number_input(
        "基本周波数 (Hz)",
        min_value=20.0,
        max_value=2000.0,
        value=440.0,
        step=1.0,
        help="ステップ0の基準周波数(デフォルト:A4 = 440 Hz)。",
    )

    num_harmonics = st.slider(
        "倍音の数",
        min_value=1,
        max_value=20,
        value=10,
        help="各音符ごとに生成する倍音(オーバートーン)の数。",
    )

# メインコンテンツエリア
st.header("和音の協和性計算機")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("入力和音")

    chord_input_help = (
        f"0から{edo - 1}までの音符インデックスを入力します。例:12-EDOの長三和音の場合は0,4,7。"
    )
    chord_input = st.text_input(
        "音符のステップをカンマ区切りで入力",
        value="0, 4, 7",
        help=chord_input_help,
    )

    # プリセットボタン
    st.write("**クイックプリセット (12-EDO):**")
    preset_col1, preset_col2, preset_col3, preset_col4 = st.columns(4)

    with preset_col1:
        if st.button("長三度"):
            chord_input = "0, 4"

    with preset_col2:
        if st.button("短三度"):
            chord_input = "0, 3"

    with preset_col3:
        if st.button("完全5度"):
            chord_input = "0, 7"

    with preset_col4:
        if st.button("短2度"):
            chord_input = "0, 1"

# 和音入力の解析
try:
    # カンマ区切りの整数を解析
    notes = [int(n.strip()) for n in chord_input.split(",")]

    if not notes:
        st.error("少なくとも1つの音符を入力してください。")
    else:
        # 協和性の計算
        try:
            roughness = calculate_consonance(
                edo=edo,
                notes=notes,
                base_frequency=base_frequency,
                num_harmonics=num_harmonics,
            )

            with col2:
                st.subheader("結果")
                st.metric(
                    label="音響的ラフネス",
                    value=f"{roughness:.4f}",
                    help="値が低いほど協和性が高い(より心地よい音)ことを示します。",
                )

                # ラフネスの解釈
                if roughness < ROUGHNESS_EXTREMELY_CONSONANT:
                    interpretation = "非常に協和的 🎶"
                    color = "green"
                elif roughness < ROUGHNESS_CONSONANT:
                    interpretation = "協和的 ✅"
                    color = "green"
                elif roughness < ROUGHNESS_SLIGHTLY_CONSONANT:
                    interpretation = "やや協和的 🎵"
                    color = "orange"
                elif roughness < ROUGHNESS_SLIGHTLY_DISSONANT:
                    interpretation = "やや不協和的 ⚠️"
                    color = "orange"
                else:
                    interpretation = "不協和的 ❌"
                    color = "red"

                st.markdown(f"**解釈:** :{color}[{interpretation}]")

            # 追加情報
            st.divider()
            st.subheader("この計算について")

            info_col1, info_col2, info_col3 = st.columns(3)

            with info_col1:
                st.metric("和音の音符数", len(notes))

            with info_col2:
                st.metric("音律システム", f"{edo}-EDO")

            with info_col3:
                num_pairs = (len(notes) * num_harmonics) * (len(notes) * num_harmonics - 1) // 2
                st.metric("分析された倍音ペアの数", f"{num_pairs:,}")

            with st.expander("i この仕組みは?"):
                st.markdown(
                    """
このアプリは、**Setharesの音響的ラフネスモデル**(1993)を使用して協和性を計算します:

1. **倍音の生成**: 各音符は、のこぎり波の音色モデルを使用して
   倍音(オーバートーン)を生成します。
2. **ラフネスの計算**: 各倍音ペアについて、以下に基づいて感覚的な不協和を計算します:
   - 周波数分離(近いほどラフネスが高い)
   - 臨界帯域幅(周波数に依存する知覚の閾値)
   - 振幅重み付け(大きい音ほどラフネスが高い)
3. **合計**: すべての倍音ペアからのラフネスを合計します。

**ラフネスが低い = 協和性が高い**

このモデルは、倍音の物理的な干渉に基づいて、なぜオクターブ(2:1の比率)が
協和的に聞こえ、短2度が不協和に聞こえるのかを説明します。
"""
                )

        except ValidationError as e:
            st.error(f"無効な入力です: {e}")
        except Exception as e:
            st.error(f"協和性の計算中にエラーが発生しました: {e}")

except ValueError:
    st.error("無効な入力形式です。カンマ区切りの整数を入力してください(例:0, 4, 7)。")

# フッター
st.divider()
st.caption(
    """
**Xenharmonic Voyager** - 12-EDOを超えたチューニングシステムの探求
Streamlitで構築 | Setharesのラフネスモデル(1993)を利用
"""
)
