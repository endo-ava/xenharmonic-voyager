"""Custom CSS styles for Xenharmonic Voyager application."""

CUSTOM_CSS = """
<style>
    /* モノスペースフォントで数学的な雰囲気 */
    .stMarkdown code {
        font-family: 'Courier New', monospace;
        font-weight: bold;
    }

    /* ボタンをグリッド状に整列 */
    .stButton > button {
        height: 65px;
        font-size: 18px;
        font-family: 'Courier New', monospace;
        font-weight: bold;
        border-radius: 4px;
        border: 2px solid rgba(128, 128, 128, 0.2);
    }

    /* 選択ボタンにグロー効果 */
    .stButton > button[kind="primary"] {
        box-shadow: 0 0 15px rgba(29, 78, 216, 0.5);
        border: 2px solid rgba(29, 78, 216, 0.8);
    }

    /* メトリクスを計測器風に */
    [data-testid="stMetricValue"] {
        font-family: 'Courier New', monospace;
        font-size: 32px;
        font-weight: 700;
        letter-spacing: 2px;
    }

    /* ヘッダーをシンプルに */
    h1, h2, h3 {
        font-weight: 600;
        letter-spacing: 1px;
    }
</style>
"""
