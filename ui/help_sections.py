"""Help sections for Xenharmonic Voyager.

このモジュールは、アプリケーションのヘルプコンテンツを提供します:
- 計算パラメータの説明
- Setharesモデルの詳細説明
"""

import streamlit as st


def render_calculation_parameters(edo: int, selected_notes: list[int], num_notes: int) -> None:
    """Render calculation parameters expander.

    Args:
        edo: N-EDO value
        selected_notes: Currently selected note indices
        num_notes: Number of notes to analyze
    """
    with st.expander("Calculation Parameters", expanded=True):
        selected_notes_display = selected_notes if selected_notes else "なし"
        st.markdown(
            f"""
            **現在の計算パラメータ:**
            - **音律システム**: {edo}-EDO
            - **選択された音**: {selected_notes_display}
            - **構成音数**: {num_notes}音
            - **使用モデル**: Sethares音響的ラフネスモデル (1993)
            - **音色モデル**: ノコギリ波 (Sawtooth Wave, 倍音振幅 = 1/k)
            - **考慮倍音数**: 第1~第10倍音
            - **基本周波数**: 440 Hz (A4)
            """
        )


def render_about_calculation() -> None:
    """Render detailed explanation of the Sethares roughness model."""
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

            #### 3.1 クリティカルバンドとラフネスの関係性

            クリティカルバンドは単なる周波数の単位ではなく、**ラフネス (不協和感) の発生メカニズム**
            に直接関係します。

            2つの音の周波数差 $\Delta f$ とクリティカルバンド幅 $CB(f)$ の**比率**
            (割り算 $\frac{\Delta f}{CB(f)}$ の値) によって、以下のようなラフネスの変化が生じます:

            - **$\Delta f = 0$ (ユニゾン)**:
              同じ周波数なので干渉なし → **ラフネス = 0** (完全協和)

            - **$\Delta f \approx 0.25 \times CB(f)$ (クリティカルバンド内)**:
              2つの音が同じクリティカルバンド内で神経レベルの干渉を起こす
              → **ラフネス = 最大** (最大不協和)

            - **$\Delta f \gg CB(f)$ (クリティカルバンドより十分離れた)**:
              聴覚系が2つの音を別々に分解できる → **ラフネス → 0** (協和)

            **重要な洞察**: ラフネスを決定するのは**絶対的な周波数差ではなく、クリティカルバンド幅
            に対する相対的な周波数差**です。これが次節で登場する「正規化された周波数差」
            $x = \frac{\Delta f}{CB(f)}$ の物理的意味です。

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
            R_{\text{total}} = \sum_{i=1}^{N \times M} \sum_{j=i+1}^{N \times M}
            R(f_i, f_j, a_i, a_j)
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

            | 音程 | ステップ | 総ラフネス |
            |------|---------|-----------|
            | 完全5度 | [0, 7] | 0.083 |
            | 長3度 | [0, 4] | 0.140 |
            | 短3度 | [0, 3] | 0.190 |
            | 短2度 | [0, 1] | 0.331 |

            このモデルは、倍音の物理的干渉に基づき、なぜ完全五度が協和的で、
            短2度が不協和なのかを定量的に説明します。

            ---

            ### 参考文献

            - **Sethares, W. A. (1993).** "Local consonance and the relationship between
              timbre and scale." *Journal of the Acoustical Society of America*, 94(3), 1218-1228.
            - **Plomp, R., & Levelt, W. J. M. (1965).** "Tonal consonance and critical bandwidth."
              *Journal of the Acoustical Society of America*, 38, 548-560.

            """
        )
