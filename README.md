# 販売支援システム テスト環境

このリポジトリは、販売支援システムの得意先管理・得意先別集計機能を Django + MySQL で検証するためのテスト環境です。得意先の登録・削除・更新、および月次 / 年次 / 商品別集計は全て MySQL (`psysdb`) 上のデータをリアルタイムに参照します。

## 環境セットアップ

1. 依存関係をインストールします。
   ```bash
   uv sync
   ```
2. MySQL コンテナを起動すると `docker/mysql/init/psysdb.sql` が自動で流し込まれます。
   ```bash
   docker compose up -d mysql
   ```
3. マイグレーションと開発サーバーを起動します。
   ```bash
   uv run manage migrate
   uv run manage runserver 0.0.0.0:8000
   ```
4. ブラウザで <http://localhost:8000/> にアクセスします。

> :information_source: 登録・削除・更新はすべて `psysdb` のテーブルに反映されます。必要に応じて `docker/mysql/init/psysdb.sql` でリセットしてください。

## 画面一覧

| 画面 | URL | 説明 |
| --- | --- | --- |
| トップ | `/` | モック概要とお知らせの表示 |
| ログイン | `/login/` | 従業員番号・パスワード入力でセッションを開始 |
| メインメニュー | `/menu/` | 各機能への導線を表示 (ログイン必須) |
| 得意先管理メニュー | `/customers/menu/` | 得意先関連機能へのショートカット |
| 得意先検索 | `/customers/search/` | 得意先コードで詳細を検索 |
| 得意先登録 | `/customers/new/` | フォーム入力を実際の得意先テーブルへ登録 |
| 得意先削除 | `/customers/delete/` | 指定コードの `delete_flag` を更新 |
| 得意先変更 | `/customers/<コード>/edit/` | 既存得意先を編集して保存 |
| 得意先一覧 | `/customers/list/` | 現在有効な得意先一覧を表示 |
| 月別受注集計 | `/reports/monthly/` | `orders` テーブルを対象に月別集計 |
| 年次受注集計 | `/reports/yearly/` | `orders` テーブルを対象に年次集計 |
| 商品別受注集計 | `/reports/by-item/` | `order_details` テーブルを対象に商品別集計 |

## ログイン方法

- `docker/mysql/init/psysdb.sql` に登録済みの従業員情報を利用してください。例: `社員番号: R20001 / パスワード: ry000001`。
- ログインに成功すると、ヘッダーに従業員情報が表示されます。ログアウトは画面右上のリンクから行えます。

## 開発メモ

- 画面スタイルは `psys/static/psys/css/app.css` にまとめています。
- バックエンドのビジネスロジックは `psys/services` 配下にまとめています。得意先関連処理は `customers.py`、集計処理は `reports.py` を参照してください。
- 実装対象機能やUI項目の詳細は `docs/app/spec.md` と `docs/app/view.md` を参照してください。
- DB を初期化したい場合は `docker/mysql/init/psysdb.sql` を流し込んでください。

今後は受注登録機能、追加のレポート、E2E テストの整備を予定しています。
