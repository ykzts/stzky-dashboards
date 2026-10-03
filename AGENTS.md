# エージェント向けガイド

このファイルは、コーディングエージェント向けの作業補助情報をまとめたものです。リポジトリの概要と表記の決まりは `README.md` を参照してください。

## 作業フロー

- ダッシュボードは Git Sync で Grafana と同期しているため、`main` へのマージがそのまま本番に反映される
- 変更前に対象の JSON と、関連する収集設定 (ykzts/stzky-infra の `services/grafana`) を確認する
- 変更は最小差分を優先し、無関係なパネルの並び替えや整形を避ける

## 検証

- 静的チェック: `python3 .github/scripts/check-dashboards.py`
- クエリを追加・変更した場合は、Grafana の API (`/api/datasources/proxy/uid/<uid>/...`) で Prometheus と Loki に対して実行し、エラーがなく値が返ることを確認する。`$__rate_interval` などの Grafana 変数は具体的な値に置き換えて実行する
- Git Sync での読み込みは、ブランチを push したあと `/apis/provisioning.grafana.app/v0alpha1/namespaces/default/repositories/<repository>/files/<path>?ref=<branch>` で確認できる

## クエリの注意点

- `rate()` などの関数はメトリクス名を落とすため、`{__name__=~"..."}` で複数のメトリクスをまとめて扱うと系列が衝突してエラーになる。`label_replace` で名前をラベルに写してからサブクエリで集計する
- 収集間隔が長いジョブ (`snmp_if` は 60 秒) に `$__rate_interval` を使うと範囲内のサンプルが足りないことがあるため、`[5m]` などの固定幅を使う

## PR 作成時の注意

- 変更したダッシュボードとパネル、変更理由を明記する
- 実施した検証 (静的チェック、クエリの実行、Git Sync での読み込み) と未実施の項目を明記する
- コミットメッセージは Conventional Commits に従う
