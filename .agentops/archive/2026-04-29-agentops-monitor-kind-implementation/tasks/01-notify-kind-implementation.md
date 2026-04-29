---
task-id: 01-notify-kind-implementation
parent-plan: ../plans/current.md
created: 2026-04-29
status: in-progress
pr-target: PR-A (notify CLI 拡張本体 + tests)
branch: claude/agentops-monitor-kind-impl-2026-04-29
---

# Task 01: `agentops-watch notify --kind` 実装本体 + 単体テスト (PR-A)

## 前提条件

- docs/18-notification-strategy.md (PR #58 マージ済) の契約を **正** とする
- docs/11-monitoring-cli.md の「実装ステータス注記」「kind→envvar マッピング表」「旧 envvar deprecated 注記」を実装で満たす
- 既存 export envvar: `DISCORD_WEBHOOK_URL_DAILLY` / `WEEKLY` / `MONTHLY` / `ANT_TIME` (`~/.bashrc`)
- 既存 `tools/agentops_monitor/__main__.py` の `cmd_check` / `build_report` / `render_text` / `load_simple_config` などは破壊しない (リファクタは最小限)
- Python 3.11+ 標準ライブラリのみ (urllib / json / argparse / pathlib / zoneinfo / unittest)
- 高リスク領域 (secret = Webhook URL) → `coding_frontier high` 以上で実装

## 不変条件

- secret (Webhook URL) を log / stdout / stderr / commit / PR / docs / コメントに **値として** 出さない
- `allowed_mentions: {"parse": []}` を **全 webhook payload に必須**
- 旧 envvar `AGENTOPS_DISCORD_WEBHOOK_URL` は **`--kind` 未指定の後方互換 path** でのみ参照する。`--kind` 指定時は **kind→envvar 固定マッピングのみ** を使用 (docs/11 §kind→envvar マッピングと一致)
- ANT_TIME 系 kind の rate-limit state は `~/.cache/agentops-watch/anttime-rate.json` (XDG_CACHE_HOME を尊重) に書き、リポジトリには **絶対に置かない**
- 単体テストでは実 webhook へ送信しない (urllib.request.urlopen を mock)
- payload に branch 名 / project 名 / `--message` を載せる前に `@everyone` / `@here` / `<@user-id>` の sanitization を行う

## 完了条件

- `tools/agentops_monitor/__main__.py` に以下を実装:
  - **`notify` サブコマンドへの引数追加**: `--kind` (choices: daily / weekly / monthly / session-start / session-end / permission-wait / alert / stop-failure)、`--message` (alert / permission-wait / stop-failure 用)、`--priority` (alert 用、default low)
  - **`KIND_TO_ENVVAR` 固定マッピング** (module 定数): docs/11 §kind→envvar マッピング表どおり
  - **`resolve_webhook_url(kind: str) -> str | None`**: kind から envvar を引き、未設定なら None。secret 値は戻り値以外で扱わない (log に出さない)
  - **`build_embed_payload(kind, report_or_message, project, branch, ...) -> dict`**: docs/18 §payload 雛形に準拠した embed format を返す。`username: "agentops-watch"`、`allowed_mentions: {"parse": []}` 必須、`fields[]` に kind 別必須項目 (docs/18 §channel 別テンプレート要件 表)
  - **`sanitize_mention_text(text: str) -> str`**: `@everyone` / `@here` / `<@&...>` / `<@!...>` / `<@...>` を `​` 挿入で無害化
  - **`AnttimeRateGuard`** クラス (or 関数群): state file `~/.cache/agentops-watch/anttime-rate.json` を読み書き、1 分 5 / 1 時間 60 を超過したら warning + skip (CLI 全体は継続)。`alert --priority high` 指定時のみ guard を bypass する選択肢を `--bypass-rate-limit` で明示提供 (デフォルト false)
  - **`send_webhook(url, payload, timeout) -> tuple[int, dict[str, str]]`**: urllib.request.urlopen で POST、HTTP 200/204 は OK、429 / 5xx は **CLI 全体を exit 2 で停止**、`Retry-After` ヘッダを state file に記録
  - **`cmd_notify` を全面書き換え**: `--kind` 必須化 (旧 envvar 後方互換 path との分岐は `if args.kind: ... else: <旧 path with deprecation warning to stderr>`)。digest 系 (daily/weekly/monthly) では `build_report` を使い、ANT_TIME 系では `--project` 単一 + `--message` ベースの payload を組む
- 旧 envvar `AGENTOPS_DISCORD_WEBHOOK_URL` 参照経路 (kind 未指定時) は **stderr に deprecation 警告** を出す。または完全撤去 (実装中に判断、撤去なら docs/11 と整合させる)
- `tools/agentops_monitor/tests/` 配下に単体テスト追加:
  - `test_resolve_webhook.py`: kind→envvar 解決 / 未設定時の None / 不正 kind での ValueError or argparse error
  - `test_payload_builder.py`: embed format / allowed_mentions 必須 / sanitization (`@everyone` 等)
  - `test_rate_guard.py`: 1 分 5 件超過で skip / 1 時間 60 件超過で skip / state file 読み書き / `--bypass-rate-limit` で bypass
  - `test_send_webhook.py`: 200 / 204 で OK / 429 で exit 2 + Retry-After 記録 / 5xx で exit 2 (urllib mock)
  - `test_cmd_notify.py`: dry-run / digest kind / ANT_TIME kind / 旧 envvar 後方互換 path の deprecation 警告
- `python3 -m compileall tools/` exit 0
- `python3 -m unittest discover tools/agentops_monitor/tests -v` 全 pass
- dry-run smoke 全 5 種 (検証手順) exit 0
- secret 値の混入 grep が 0 件 (`grep -rn 'discord.com/api/webhooks/' .` で実 URL 不在)
- Codex `review_frontier --effort high` cross-review で P0/P1 0 件
- archive 移動 + commit + push + PR-A 作成

## 禁止事項

- 実 Webhook URL を log / commit / PR / docs / コメントに値として出すこと
- 単体テストで実 webhook へ送信すること (mock 必須)
- `~/.cache/` 以外の場所 (リポジトリ内 / `.agentops/` 内) に rate-limit state を保存すること
- `cmd_check` や `build_report` の既存仕様を変更すること (本 task のスコープ外)
- `~/.claude/hooks/` の実 hook ファイルを生成・編集すること
- crontab を編集 / 反映すること
- `~/dotfiles/bin/notify-pending-discord.sh` の中身を変更すること
- 公式 Discord plugin の MCP 設定を変更すること

## 停止条件

- レビュー修正が 2 周を超える → ユーザー確認
- Webhook URL 値が誤って混入 → 即停止
- Discord API の仕様変更で `allowed_mentions` 等の項目が deprecated → ユーザー確認 (Context7 / 公式 docs で再確認)
- urllib.request の Retry-After 解釈で公式仕様と食い違う → docs/18 §ANT_TIME 頻度上限ガード とユーザー確認
- mock なしで実 webhook 送信が必要になる事象 → 設計変更してテスト可能化、無理ならユーザー確認
- ANT_TIME state file の concurrent write 競合 → 単一プロセス前提を docs に明記し、ユーザー確認
- スコープ外への踏み込み (hook / cron / localize)

## 検証手順

1. `python3 -m compileall tools/`
2. `python3 -m unittest discover tools/agentops_monitor/tests -v`
3. `cd /home/otaku/agentops && python3 scripts/agentops-watch notify --kind daily --projects config/projects.yml --dry-run` → embed JSON が stdout に出る
4. `python3 scripts/agentops-watch notify --kind alert --message "smoke" --dry-run` → embed JSON
5. `python3 scripts/agentops-watch notify --kind session-start --project /home/otaku/agentops --dry-run` → embed JSON
6. `python3 scripts/agentops-watch notify --kind permission-wait --project /home/otaku/agentops --message "Bash" --dry-run` → embed JSON
7. `python3 scripts/agentops-watch notify --kind stop-failure --project /home/otaku/agentops --message "test" --dry-run` → embed JSON
8. `python3 scripts/agentops-watch notify --dry-run --projects config/projects.yml` (旧 path) → deprecation 警告 stderr + 旧形式 content payload
9. `grep -rn 'AGENTOPS_DISCORD_WEBHOOK_URL' tools/ docs/ scripts/ rules/ skills/ workflows/ templates/ config/ 2>/dev/null` → 後方互換 path の参照のみ残る
10. `grep -rn 'discord.com/api/webhooks/' .` → 0 件 (テストの dummy URL は `discord.invalid` を使う)
11. agentops-reviewer subagent で独立レビュー (correctness / security / tests)
12. `scripts/agentops delegate --to codex --role review_frontier --effort high --input tools/agentops_monitor/__main__.py` で cross-review
13. P0/P1 反映後、reviewer 再走で 0 件確認
14. `scripts/agentops archive task --task-id 01-notify-kind-implementation --dry-run` → 本番実行
15. commit → push → PR-A 作成 (`gh pr create`) → AI auto-merge 許諾条件評価 → squash merge → main 同期

## DbC

- **適用前提**: docs/18 / docs/11 の契約変更なし、Python 3.11+ 標準ライブラリのみ、`cmd_check` 既存挙動を破壊しない
- **適用不変**: secret 値非露出、allowed_mentions 必須、test 経路で実 HTTP 不発生、rate-limit state はホスト local
- **適用完了**: 上記「完了条件」全項目
- **適用禁止**: 上記「禁止事項」記載
- **適用停止**: 上記「停止条件」のいずれか発生
