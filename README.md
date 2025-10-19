# Xenharmonic Voyager

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://xenharmonic-voyager.streamlit.app/)
[![CI](https://github.com/endo-ava/xenharmonic-voyager/actions/workflows/ci.yml/badge.svg)](https://github.com/endo-ava/xenharmonic-voyager/actions/workflows/ci.yml)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

**N-EDO(N平均律)の音響空間を探求するための実験的Webアプリケーション**

Setharesの音響ラフネスモデルに基づき、和音の協和度をリアルタイムで計算・可視化します。

## 概要 (Overview)

Xenharmonic Voyagerは、12平均律以外の音響宇宙（Xenharmonic）を探求するためのインタラクティブな可視化ツールです。様々なN-EDO(Equal Divisions of the Octave, N平均律)における和音の音響特性を分析できます。

従来の音楽理論アプリが12音平均律に焦点を当てているのに対し、本アプリケーションは代替チューニングシステムの音響特性を探求します。文化的慣習や主観的判断に頼らず、Setharesの音響ラフネスモデルによる客観的で物理学ベースの協和度測定を提供します。

### コアコンセプト

- **「観測装置」としての役割**: 楽器や作曲ツールではなく、音響現象を観測・分析するための実験装置
- **物理モデルへの忠実さ**: ヘルムホルツやSetharesらが提唱した音響心理学モデルに基づいた、客観的で定量的な協和度の算出
- **"Xenharmonic"の精神**: 単に音程が細かい(Microtonal)のではなく、未知の響きの法則を探求する冒険的思想

## 主要機能 (Features)

### 協和度計算
- **N-EDO対応**: 12-EDO、19-EDOなど様々な平均律に対応
- **リアルタイム計算**: Sethares (1993) の音響ラフネスモデルを実装
- **科学計算**: NumPyによる高速な倍音列計算

### 可視化機能
- **不協和度曲線 (Dissonance Curve)**: 選択したN-EDOにおける全音程の協和度分布を可視化
- **インタラクティブグラフ**: Plotlyによる動的なデータ探索
- **分析履歴**: 過去の分析結果を時系列で記録・表示

### インタラクティブUI
- **Streamlit**: 直感的な操作環境
- **リアルタイムフィードバック**: パラメータ変更に即座に応答
- **比較機能**: 12-EDO長三和音との協和度比較

## 技術スタック (Technology Stack)

### アプリケーション本体

| 技術 | バージョン | 用途 |
| :--- | :--- | :--- |
| **Python** | 3.13+ | アプリケーション全体の記述言語 |
| **Streamlit** | 最新版 | インタラクティブなUI構築 |
| **NumPy** | 最新版 | 高速な数値計算・配列演算 |
| **Pydantic** | 最新版 | データ検証と型安全性 |
| **Plotly** | 5.18.0+ | インタラクティブなグラフ可視化 |

### 開発ツール

| 技術 | 用途 |
| :--- | :--- |
| **uv** | Python依存管理・仮想環境・バージョン管理 |
| **Ruff** | 超高速Linter/Formatter |
| **Pytest** | テストフレームワーク |
| **mypy** | 静的型チェッカー |
| **pre-commit** | Gitフック管理 |

### デプロイ

- **Streamlit Community Cloud**: アプリケーションホスティング

## プロジェクト構成 (Project Structure)

```
xenharmonic-voyager/
├── app.py                      # Streamlitメインアプリケーション
├── src/
│   ├── application/            # Application Layer
│   │   ├── dto.py              #   - 入力検証（Pydantic）
│   │   └── use_cases.py        #   - ユースケース実行
│   ├── domain/                 # Domain Layer
│   │   ├── constants.py        #   - ドメイン定数
│   │   ├── models.py           #   - Value Objects
│   │   ├── protocols.py        #   - インターフェース定義
│   │   ├── acoustics.py        #   - 音響計算ロジック
│   │   └── services.py         #   - Domain Service
│   └── visualization/          # Presenter Layer
│       ├── dissonance_curve.py #   - 不協和曲線
│       ├── analysis_presenter.py #   - 分析ビュー
│       └── history_presenter.py  #   - 履歴ビュー
├── ui/                         # UI Layer: Streamlit View Components
├── tests/                      # テストコード
├── docs/                       # プロジェクトドキュメント
│   ├── 00.project/             # プロジェクト定義
│   ├── 10.domain/              # ドメイン知識
│   ├── 20.development/         # 開発ガイド
│   └── 70.knowledge/           # ナレッジベース
├── .pre-commit-config.yaml     # pre-commitフック設定
├── ruff.toml                   # Ruff設定
├── pytest.ini                  # Pytest設定
├── pyproject.toml              # プロジェクトメタデータと依存関係
└── justfile                    # タスクランナー設定
```

### アーキテクチャ (Architecture)

本プロジェクトは**Clean Architectureの原則**に基づいた**3層構造**を採用しています:

1. **UI層** (`app.py`, `ui/`, `src/visualization/`): Streamlit UI、Presenter、ViewModel
2. **Application層** (`src/application/`): Use Case、入力検証
3. **Domain層** (`src/domain/`): ビジネスロジック、ドメインモデル、音響計算

**特徴**:
- シンプルで実用的な設計（過剰な抽象化を回避）
- 明確な責務分離（各層が独立してテスト可能）
- 依存性の一方向性（UI → Application → Domain）

詳細は [`docs/20.development/2001.architecture-implementation.md`](docs/20.development/2001.architecture-implementation.md) を参照してください。

---

## 協和度計算の原理 (Calculation Model)

### 基本モデル

本アプリケーションは、**Sethares (1993)** の音響ラフネスモデルを採用しています:

- 倍音間の周波数差とクリティカルバンド幅 (Critical Bandwidth) の関係から、音響的な「粗さ (Roughness)」を定量化
- **ラフネスが低い = 協和的**、**ラフネスが高い = 不協和的** と評価されます

### パラメータ

- **倍音減衰**: ノコギリ波モデル (k番目の倍音振幅 = 1/k)
- **考慮倍音数**: 第1〜第10倍音 (計算負荷と知覚的重要性のバランス)
- **クリティカルバンド**: Plomp-Levelt式 `CB(f) ≈ 0.24 × f + 25 Hz`

### 数学的定義

詳細な数式と理論的背景は [`docs/10.domain/1001.mathematical-foundation.md`](docs/10.domain/1001.mathematical-foundation.md) を参照してください。

## 参考文献 (References)

- Sethares, W. A. (1993). "Local consonance and the relationship between timbre and scale." *Journal of the Acoustical Society of America*, 94(3), 1218-1228.
- Helmholtz, H. von (1877). *On the Sensations of Tone*
- Plomp, R., & Levelt, W. J. M. (1965). "Tonal consonance and critical bandwidth." *Journal of the Acoustical Society of America*, 38, 548-560.

## リンク (Links)

- [https://xenharmonic-voyager.streamlit.app/](https://xenharmonic-voyager.streamlit.app/)
