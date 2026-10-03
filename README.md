# stzky-dashboards

[graph.stzky.com](https://graph.stzky.com) の Grafana ダッシュボードを管理するリポジトリです。Grafana の Git Sync でこのリポジトリと同期しています。

## ダッシュボード

| ファイル | タイトル | 内容 |
| --- | --- | --- |
| `stzky-overview.json` | stzky overview | 自宅サーバーと周辺機器の概況 (監視対象の状態、ホスト、コンテナ、ルーター、ログ、監視基盤) |
| `immich.json` | immich | 写真・動画ライブラリ (Immich) の状態 |

データの収集設定 (Prometheus、Alloy、snmp_exporter など) は [ykzts/stzky-infra](https://github.com/ykzts/stzky-infra) の `services/grafana` で管理しています。

## Git Sync

- 同期対象は `main` ブランチで、60 秒ごとに Grafana へ反映されます
- フォルダーは使わず (`folderless`)、リポジトリ直下のファイルが Grafana のトップレベルに並びます
- Grafana 側の変更はブランチへの保存だけを許可しているため、UI で編集した場合も Pull Request を経由して `main` に入ります

## 変更の流れ

1. ブランチを作成して JSON を編集する (または Grafana の UI で編集してブランチに保存する)
2. `python3 .github/scripts/check-dashboards.py` で静的チェックを行う
3. Pull Request を作成する。CI (`Check / Dashboards`) が同じチェックを実行します
4. マージ後、Git Sync が Grafana に反映します

`check-dashboards.py` は JSON の構文、uid とタイトルの重複、パネルの重なり、未知のデータソース、`stzky` の表記を確認します。クエリの実行結果は確認しないため、クエリを変更した場合は Grafana の API で実際のデータソースに対して実行してから Pull Request を作成してください。

## 表記の決まり

- `stzky` は常に小文字で書きます (`Stzky` とは書きません)
- パネルや行のタイトルには、何を表示しているかを書き、収集ツール名 (cAdvisor、Loki、Prometheus など) は書きません。機器の型番 (RTX1300 など) は書いて構いません
- 複数系列のパネルは `palette-classic-by-name` を使い、系列が増減しても色が変わらないようにします
