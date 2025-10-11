# Xenharmonic Voyager

# 概要

- **目的**: N-EDO(N Equal Divisions of the Octave, N平均律)の音響空間を探求する実験的なWebアプリ。
- **機能**: N-EDOにおける音程や和音の「協和度」を、Setharesの音響心理学モデルに基づきリアルタイムで計算・可視化する。
- **思想**: 響きの美しさを、慣習ではなく物理的な倍音の干渉（ラフネス）から定量的に探求する観測装置。
- 詳しくは要件定義書(`0001.requirements.md`)を参照

# 技術スタック

- **本体**: Python v3.13, Streamlit, NumPy, Pydantic
- **開発**: uv, Ruff, pre-commit, Pytest, mypy, Git/GitHub
- **デプロイ**: Streamlit Community Cloud

# 主要開発コマンド

`just` の利用を推奨 (`just --list`で一覧表示)。

| 目的 | Just コマンド | `uv` 直接実行 |
| :--- | :--- | :--- |
| **開発サーバ起動** | `just dev` | `uv run streamlit run app.py` |
| **テスト** | `just test` | `uv run pytest --cov=src` |
| **Commit準備** | `just prepare` | `uv run pre-commit run --all-files` (2回実行) |
| **Lint** | `just lint` | `uv run ruff check .` |
| **Format** | `just fix` | `uv run ruff format .` |


# ドキュメント駆動開発

**重要原則: ドキュメントは、信頼できる唯一の情報源 (Single Source of Truth) です。**

1.  **参照の徹底 (Read First)**: 何かを作成・変更する前には、関連ドキュメントを読み、その内容を尊重。Serena memory読み込みも可。
2.  **同期の維持 (Sync Docs)**: コード変更が設計や規約に影響する場合、**必ず**ドキュメントの更新も同時に提案。Serena memoryとの同期も同様。
3.  **知識の集約 (Accumulate Knowledge)**: 開発で得た新たな知見は、`docs/70.knowledge/` に追記することを積極的に提案。

## ドキュメント体系

- **番号体系**: `00xx`:プロジェクト, `10xx`:ドメイン, `20xx`:開発, `30xx`:品質, `70xx`:ナレッジ
- **主要ドキュメント**:
    - `0001.requirements.md`: 要件定義書
    - `0002.screenDesignes.md`: 画面設計書
    - `1001.mathematical-foundation.md`: 協和度計算の数学的基盤
    - `2001.architecture-implementation.md`: アーキテクチャと実装詳細

# 開発ワークフロー

作業はこのフローに沿って進める。

1.  **Phase 1: 企画**: Issueを理解する (何を、なぜ作るか)。
2.  **Phase 2: 設計**: 実装方法を決定する (どう作るか)。
3.  **Phase 3: 実装**: 設計に基づき、クリーンなコードを書く。
4.  **Phase 4: 品質保証**: テストを書き、品質を保証する。
5.  **Phase 5: レビュー**: 第三者の視点でコードを評価し、マージする。
6.  **Phase 6: ドキュメント更新**: 変更内容をドキュメントに反映し、知識を共有する。

**継続的プロセス**: 開発全体を通じて、常にリファクタリングを意識し、コードの健全性を維持してください。

# コーディングスタイル

本プロジェクトは、一貫性と可読性を維持するため、以下の規約に基づく。

- **基本規約**: [PEP 8 -- Style Guide for Python Code](https://peps.python.org/pep-0008/) に準拠。
- **フォーマッター**: コードフォーマットは [Ruff Formatter](https://docs.astral.sh/ruff/formatter/) を使用。
- **リンター**: 静的解析は [Ruff Linter](https://docs.astral.sh/ruff/linter/) を使用。設定は `ruff.toml` を参照。
- **型ヒント**: [PEP 484](https://peps.python.org/pep-0484/) に基づき、すべての関数・メソッドに型ヒントを付与。静的型チェックには `mypy` を使用。
- **命名規則**:
    - `snake_case`: 変数、関数、メソッド
    - `PascalCase`: クラス
    - `UPPER_SNAKE_CASE`: 定数
- **Docstring**: [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html#3.8-comments-and-docstrings) に準拠したdocstringを記述し、関数やクラスの目的、引数、戻り値を明確にします。

# Git & Pull Request 規約

- **ブランチ**:
    - **戦略**: GitHub Flow (`main`への直接コミット禁止)。
    - **命名**: `<type>/<short-description>` (例: `feat/add-playback`、`refactor/ui-sidebar`)。
- **コミット**:
    - **規約**: Conventional Commits (`<type>: <subject>`)。
    - **主な `<type>`**: `feat`,`fix`,`docs`,`style`,`refactor`,`test`,`chore`
    - **言語**: **英語**
- **Pull Request (PR)**:
    - **単位**: 1 PR = 1関心事。巨大化させない。
    - **記述**: テンプレートを必ず使用。Descriptionにはそのブランチの変更内容を全て網羅。
- **レビュー**:
    - レビューは鵜呑みにせず、要否を自身で判断し、不要な場合は理由を伝える。
- **言語**:
    - **日本語**: コードコメント、PR/Issue、レビュー。
    - **英語**: コミットメッセージ。

# MCP (Model Context Protocol) Servers

プロジェクトの開発を支援するために、以下のMCPサーバーが設定されている。

| MCPサーバー名 | 目的 | 主な利用シーン |
| :--- | :--- | :--- |
| **playwright** | ブラウザ操作の自動化 | 画面の動作確認、高難度バグの原因調査、エビデンススクリーンショット撮影 |
| **serena** | コードの静的解析・操作、<br>プロジェクト知識の管理 | シンボル検索等の高度なコード理解。常時使用推奨<br>過去の設計判断やドキュメント（メモリ）の参照 |
| **context7** | 外部技術情報の検索 | ライブラリのバージョン違いによる仕様の検索など |
| **github** | GitHubリポジトリとの連携 | Issue/PR/PR Reviewの作成・管理 |
| **sequential-thinking** | 計画的な問題解決の支援 | 複雑な思考が必要と判断した際の体系的な思考サポート |
