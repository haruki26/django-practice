---
applyTo: '**'
---

## プロジェクト概要

このプロジェクトは、販売支援システムの開発を目的としています。

各ドキュメントは以下を参照してください。

- [プロジェクト仕様書](./../../docs/app/spec.md)
- [テーブル定義書](./../../docs/app/tables.md)
- [画面仕様書](./../../docs/app/view.md)

## 開発環境

GitHubで管理を行います。
ファイルのリネームや移動を行う場合は、`git mv`コマンドを使用してください。

主な技術スタック（一部抜粋）は以下の通りです。

### フロントエンド

- HTML
- CSS
- Vanilla JavaScript

### バックエンド

- Python 3.13
- Django 4.2
- MySQL 8.0

---

開発時の依存関係として、以下のツールを使用します。

- プロジェクト管理: uv
- フォーマッタ兼リンター: ruff
- 型チェッカー: pyright
- タスクランナー: taskipy

### コマンド集

taskipyを使用して、以下のコマンドを実行できます。

```bash
# フォーマット
uv run task fmt

# 型チェック
uv run task type

# 開発サーバー起動
uv run task dev
```

その他のコマンドは、[pyproject.toml](./../../pyproject.toml)の`[tool.taskipy.tasks]`セクションを参照してください。
