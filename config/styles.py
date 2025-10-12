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
        width: 110%;
        height: 50px;
        border-radius: 4px;
        border: 2px solid rgba(128, 128, 128, 0.2);
    }

    /* ボタン内のテキストにもフォントサイズを確実に適用 */
    .stButton > button p,
    .stButton > button div {
        font-size: 12px !important;
        font-family: 'Courier New', monospace;
        font-weight: bold;
    }

    /* 選択ボタンを青系統に変更 */
    .stButton > button[kind="primary"] {
        background-color: #1d4ed8 !important;
        color: white !important;
        box-shadow: 0 0 15px rgba(29, 78, 216, 0.5);
        border: 2px solid rgba(29, 78, 216, 0.8);
    }

    /* ホバー時も青系統を維持 */
    .stButton > button[kind="primary"]:hover {
        background-color: #2563eb !important;
        border: 2px solid rgba(37, 99, 235, 0.9);
    }

    /* ヘッダーをシンプルに */
    h1, h2, h3 {
        font-weight: 600;
        letter-spacing: 1px;
    }
</style>
"""
