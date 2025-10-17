"""ui/analysis_view.py のStreamlit AppTest統合テスト

このテストは、AnalysisViewModelを受け取って正しくUIレンダリングされることを検証します。
Streamlitの AppTest フレームワークを使用して、実際のUIコンポーネントの動作を確認します。
"""

import pytest
from streamlit.testing.v1 import AppTest

from src.visualization.analysis_presenter import AnalysisViewModel


@pytest.fixture
def analysis_app():
    """Analysis view用のテストアプリを作成"""
    # テスト用のStreamlitアプリケーションコードを文字列で定義
    app_script = """
import streamlit as st
from src.visualization.analysis_presenter import AnalysisViewModel
from ui.analysis_view import render_analysis_view

# テスト用のViewModelを作成(session_stateから取得)
view_model = st.session_state.get('test_view_model')
if view_model:
    render_analysis_view(view_model)
"""
    return AppTest.from_string(app_script)


class TestRenderAnalysisView:
    """render_analysis_view関数のStreamlit統合テスト"""

    def test_renders_very_consonant_display(self, analysis_app):
        """非常に協和的なケースの表示"""
        vm = AnalysisViewModel(
            roughness=0.1, roughness_level="L1 (Very Consonant)", inverted_progress=0.95
        )

        analysis_app.session_state["test_view_model"] = vm
        analysis_app.run()

        # Roughness Analysisヘッダーが表示されている
        assert len(analysis_app.markdown) > 0
        assert any("Roughness Analysis" in str(md.value) for md in analysis_app.markdown)

        # メトリクスが表示されている
        assert len(analysis_app.metric) > 0
        metric = analysis_app.metric[0]
        assert "R(S)" in metric.label
        assert "0.100000" in metric.value

        # キャプションが表示されている
        assert len(analysis_app.caption) > 0
        assert any("L1 (Very Consonant)" in str(cap.value) for cap in analysis_app.caption)

    def test_renders_dissonant_display(self, analysis_app):
        """不協和的なケースの表示"""
        vm = AnalysisViewModel(
            roughness=5.0, roughness_level="L5 (Dissonant)", inverted_progress=0.0
        )

        analysis_app.session_state["test_view_model"] = vm
        analysis_app.run()

        # メトリクス値が正しい
        metric = analysis_app.metric[0]
        assert "5.000000" in metric.value

        # キャプションにレベルが表示されている
        assert len(analysis_app.caption) > 0
        assert any("L5 (Dissonant)" in str(cap.value) for cap in analysis_app.caption)

    def test_displays_consonance_level_caption(self, analysis_app):
        """協和度レベルのキャプションが表示される"""
        vm = AnalysisViewModel(
            roughness=1.0, roughness_level="L3 (Slightly Consonant)", inverted_progress=0.5
        )

        analysis_app.session_state["test_view_model"] = vm
        analysis_app.run()

        # キャプションにレベルが含まれている
        assert len(analysis_app.caption) > 0
        caption_texts = [str(cap.value) for cap in analysis_app.caption]
        assert any("L3 (Slightly Consonant)" in text for text in caption_texts)

    def test_metric_has_help_text(self, analysis_app):
        """メトリクスにヘルプテキストが設定されている"""
        vm = AnalysisViewModel(
            roughness=0.5, roughness_level="L2 (Consonant)", inverted_progress=0.75
        )

        analysis_app.session_state["test_view_model"] = vm
        analysis_app.run()

        metric = analysis_app.metric[0]
        assert metric.help is not None
        assert "ラフネス" in metric.help

    def test_two_column_layout(self, analysis_app):
        """2カラムレイアウトが使用されている"""
        vm = AnalysisViewModel(
            roughness=0.5, roughness_level="L2 (Consonant)", inverted_progress=0.75
        )

        analysis_app.session_state["test_view_model"] = vm
        analysis_app.run()

        # メトリクスとキャプションが表示されている(2カラムレイアウトの証明)
        assert len(analysis_app.metric) == 1
        assert len(analysis_app.caption) == 1
        # columnsの使用を確認(カラムレイアウトが使われている)
        assert len(analysis_app.columns) > 0
