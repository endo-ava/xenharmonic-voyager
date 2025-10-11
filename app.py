"""Xenharmonic Voyager - メインStreamlitアプリケーション

このモジュールは、Setharesの音響的ラフネスモデルを使用して、
異種調和の協和性を探求するためのユーザーインターフェースを提供します。
"""

import streamlit as st
from pydantic import ValidationError

from config.styles import CUSTOM_CSS
from src.calculator import calculate_consonance
from ui import render_sidebar, render_step_selector
from ui.analysis_view import render_analysis_view
from ui.history_view import record_observation, render_history_view
from ui.step_selector import render_selection_status

# ===== Page Configuration =====
st.set_page_config(
    page_title="Xenharmonic Voyager",
    page_icon="🎵",
    layout="wide",
)

# ===== Custom CSS =====
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ===== Helper Functions =====
def initialize_session_state() -> None:
    """Initialize session state"""
    defaults = {
        "edo": 12,
        "num_notes": 3,
        "selected_notes": [],
        "reference_score": None,
        "max_score": None,
        "observation_history": [],
        "pinned_observations": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ===== Initialize =====
initialize_session_state()

# ===== Title and Description =====
st.title("Xenharmonic Voyager")
st.markdown(
    """
    N-EDOにおいて任意の数の音を選択し、その響きの「協和度」を
    **Setharesの音響的ラフネスモデル**でリアルタイムに計算・可視化します。
    """
)

# ===== Sidebar: Parameters =====
edo, num_notes = render_sidebar()

# ===== Main Area: Step Selection =====
render_step_selector(edo, st.session_state.selected_notes, num_notes)
render_selection_status(edo, st.session_state.selected_notes)

# ===== Analysis and History =====
if len(st.session_state.selected_notes) == num_notes:
    try:
        # Calculate roughness
        current_roughness = calculate_consonance(
            edo=st.session_state.edo,
            notes=st.session_state.selected_notes,
        )

        # 基準値の計算 (初回のみ)
        if st.session_state.reference_score is None:
            st.session_state.reference_score = calculate_consonance(
                edo=12,
                notes=[0, 4, 7],  # 12-EDO 長三和音
            )

        # 最大値の計算 (初回のみ)
        if st.session_state.max_score is None:
            st.session_state.max_score = calculate_consonance(
                edo=12,
                notes=[0, 1],  # 12-EDO 短2度
            )

        # Render analysis results
        render_analysis_view(current_roughness)

        # Record and render history
        record_observation(st.session_state.edo, st.session_state.selected_notes, current_roughness)
        render_history_view()

    except ValidationError as e:
        st.error(f"Validation Error: {e}")
    except Exception as e:
        st.error(f"Calculation Error: {e}")

# ===== Detail Information =====
st.divider()

# Calculation Parameters
with st.expander("Calculation Parameters", expanded=True):
    st.markdown(
        f"""
        **現在の計算パラメータ:**
        - **音律システム**: {st.session_state.edo}-EDO
        - **選択された音**: {
            st.session_state.selected_notes if st.session_state.selected_notes else "なし"
        }
        - **構成音数**: {st.session_state.num_notes}音
        - **使用モデル**: Sethares音響的ラフネスモデル (1993)
        - **音色モデル**: ノコギリ波 (Sawtooth Wave, 倍音振幅 = 1/k)
        - **考慮倍音数**: 第1~第10倍音
        - **基本周波数**: 440 Hz (A4)
        """
    )

# About This Calculation
with st.expander("About This Calculation"):
    st.markdown(
        """
        ## Setharesの音響的ラフネスモデル

        このアプリケーションは、**Sethares (1993)** の音響的ラフネスモデルを使用して、
        和音の協和性を物理的・客観的に計算します。

        ### 計算の流れ

        1. **倍音の生成**
           各音符は、ノコギリ波の音色モデルを使用して倍音列を生成します。
           第k倍音の振幅は `1/k` で減衰します。

        2. **ラフネスの計算**
           すべての倍音ペアについて、以下に基づいて音響的ラフネスを計算します:
           - **周波数差**: 倍音同士の周波数が近いほどラフネスが高い
           - **臨界帯域幅 (Critical Bandwidth)**: 周波数に依存する知覚の閾値
           - **振幅**: 大きい音同士が干渉するほどラフネスが高い

        3. **合計**
           すべての倍音ペアからのラフネスを合計し、和音全体の協和度スコアとします。

        ### 協和度の解釈

        - **ラフネスが低い = 協和性が高い** (心地よく響く)
        - **ラフネスが高い = 不協和性が高い** (濁った響き)

        このモデルは、倍音の物理的な干渉に基づいて、なぜオクターブ (2:1の比率) が
        協和的に聞こえ、短2度が不協和に聞こえるのかを説明します。

        ### 参考文献

        - Sethares, W. A. (1993). "Local consonance and the relationship between timbre and scale."
          *Journal of the Acoustical Society of America*, 94(3), 1218-1228.
        """
    )

# Footer
st.divider()
st.caption(
    """
    **Xenharmonic Voyager** - 12-EDOを超えたチューニングシステムの探求
    Streamlitで構築 | Setharesのラフネスモデル (1993) を利用
    """
)
