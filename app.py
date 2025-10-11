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
        r"""
        ## Setharesの音響的ラフネスモデル

        このアプリケーションは、**Sethares (1993)** の音響的ラフネスモデルを使用して、
        和音の協和性を物理的・客観的に計算します。

        ---

        ### 1. N-EDO音律理論

        N-EDO (N-Equal Divisions of the Octave) は、オクターブをN個の等しい音程に分割する
        音律システムです。

        #### 周波数計算式

        第 $n$ ステップの周波数 $f(n)$ は、基準周波数 $f_{\text{base}}$ から以下の式で
        計算されます:

        $$
        f(n) = f_{\text{base}} \times 2^{n/N}
        $$

        - $f_{\text{base}} = 440$ Hz (A4)
        - $N$: オクターブの分割数 (例: 12-EDO、19-EDOなど)
        - $n$: ステップインデックス (0からN-1)

        **例** (12-EDO、完全5度): $f(7) = 440 \times 2^{7/12} \approx 659.25$ Hz

        ---

        ### 2. 倍音列生成 (ノコギリ波モデル)

        実際の楽器音は、基音だけでなく整数倍の周波数を持つ**倍音 (harmonics)** を含みます。
        本アプリでは、ノコギリ波の音色モデルを採用しています。

        #### 倍音の振幅減衰則

        第 $k$ 倍音の周波数と振幅:

        $$
        f_k = k \times f_0, \quad a_k = \frac{1}{k} \quad (k = 1, 2, 3, \ldots, 10)
        $$

        | 倍音次数 | 周波数 | 振幅 |
        |---------|--------|------|
        | 1 | $f_0$ | 1.0 |
        | 2 | $2f_0$ | 0.5 |
        | 3 | $3f_0$ | 0.333 |
        | 10 | $10f_0$ | 0.1 |

        この**1/k減衰則**により、自然な音色の特性が再現されます。

        ---

        ### 3. クリティカルバンド幅理論

        **クリティカルバンド幅 (Critical Bandwidth, CB)** は、聴覚系が周波数を分解できる
        最小単位です。2つの音が同じクリティカルバンド内に存在すると、神経レベルで干渉し、
        ラフネス (粗さ) として知覚されます。

        #### Plomp & Levelの線形近似式

        本実装では、計算効率と精度のバランスを考慮し、以下の線形近似式を使用しています:

        $$
        CB(f) = 0.24 \times f + 25 \text{ Hz}
        $$

        **例**: 440 Hz (A4) のクリティカルバンド幅 = $0.24 \times 440 + 25 \approx 130.6$ Hz

        ---

        ### 4. ラフネス計算 (Setharesモデル)

        #### 4.1 ディソナンス曲線

        2つの純音間のディソナンス (不協和度) は、以下の曲線でモデル化されます:

        $$
        g(x) = e^{-3.5x} - e^{-5.75x}
        $$

        ここで、$x = \frac{\Delta f}{CB(f_{\min})}$ は正規化された周波数差です。

        **曲線の特徴**:
        - $x = 0$ (ユニゾン): ディソナンス = 0
        - $x \approx 0.24$: 最大ディソナンス
        - $x$ が大きい: ディソナンス → 0 (協和)

        #### 4.2 ペアワイズラフネス

        2つの倍音 $(f_1, a_1)$ と $(f_2, a_2)$ 間のラフネス:

        $$
        R(f_1, f_2, a_1, a_2) = a_1 \times a_2 \times g\left(
        \frac{|f_2 - f_1|}{CB(\min(f_1, f_2))} \right)
        $$

        振幅積 $a_1 \times a_2$ により、両音の音量に応じてラフネスがスケールされます。

        #### 4.3 総ラフネスの計算

        和音の総ラフネス $R_{\text{total}}$ は、**すべての異なる倍音ペア**のラフネスの
        総和です:

        $$
        R_{\text{total}} = \sum_{i=1}^{N \times M} \sum_{j=i+1}^{N \times M} R(f_i, f_j, a_i, a_j)
        $$

        - $N$: 和音の構成音数
        - $M$: 各音の倍音数 (本実装では10)

        **計算例** (3和音、10倍音):
        - 総倍音数: $3 \times 10 = 30$
        - ペア数: $\binom{30}{2} = 435$ ペア

        ---

        ### 5. 協和度の解釈

        - **ラフネスが低い = 協和性が高い** (心地よく響く)
        - **ラフネスが高い = 不協和性が高い** (濁った響き)

        #### 代表的な音程の例 (12-EDO基準)

        | 音程 | ステップ | 総ラフネス | 評価 |
        |------|---------|-----------|------|
        | 完全5度 | [0, 7] | 0.083 | 協和的 |
        | 長3和音 | [0, 4, 7] | 0.370 | 協和的 |
        | 短2度 | [0, 1] | 0.331 | 不協和的 |

        このモデルは、倍音の物理的干渉に基づき、なぜオクターブ (2:1) が協和的で、
        短2度が不協和なのかを定量的に説明します。

        ---

        ### 参考文献

        - **Sethares, W. A. (1993).** "Local consonance and the relationship between
          timbre and scale." *Journal of the Acoustical Society of America*, 94(3), 1218-1228.
        - **Plomp, R., & Levelt, W. J. M. (1965).** "Tonal consonance and critical bandwidth."
          *Journal of the Acoustical Society of America*, 38, 548-560.

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
