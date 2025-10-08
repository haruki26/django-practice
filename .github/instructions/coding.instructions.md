---
applyTo: '**/*.py'
---

## フォーマットと静的解析

フォーマッタ、リンターは `Ruff` を使用する。設定は [.ruff.toml](./../../.ruff.toml) に従うこと。

- コードを変更、作成した時にリントエラーが発生した場合、まずは `uv run task fmt` でフォーマットとチェックを実行し、自動修正を試みること
- それでも解消しない場合は、リントエラーの内容を確認し、適切にコードを修正すること

## 型ヒント

- 全ての関数・メソッドの引数と戻り値に型ヒントを付与すること。
- typingモジュールのAny、castの使用は最小限に留めること。

## 命名規則

Pythonの命名規則に従うこと。

- 変数・関数: snake_case
- クラス: PascalCase
- 定数: UPPER_SNAKE_CASE

## コメントとDocstring

全ての公開クラスと関数には、GoogleスタイルのDocstringを記述すること。

複雑なロジックには処理内容を説明するコメントを記述すること。

## エラーハンドリング

`try...except`ブロックでは具体的な例外を捕捉し、`except Exception`は避けること。

exceptionのメッセージは具体的で問題の特定に役立つ情報を含め、`logger.exception`を使用してログに記録すること。

## ロギング

ロギングには[`utils/log_config](./../../django_project/utils/logger.py)で定義されている`logger`を使用すること。

```python
from utils.logger import get_logger

logger = get_logger(__name__)

# ログ出力例
logger.info("情報メッセージ")
```

DEBUG、INFO、WARNING、EXCEPTIONなどログレベルを適切に使い分け、デバッグや問題追跡に役立つ情報を出力すること。

## その他の注意点

- 名前空間の汚染を避けるため、`__init__.py`では必要なクラスや関数のみをエクスポートすること。
  - パッケージ中で定義されている全てのクラスや関数を`__init__.py`でエクスポートする必要はない。
