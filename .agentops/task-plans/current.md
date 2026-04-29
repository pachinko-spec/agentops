---
session: 2026-04-29
parent-plan: ../plans/current.md
status: in-progress
---

# Task Plan: `agentops-watch notify --kind` 実装本セッション

## 今回セッションの実行順

1. **task 01 (PR-A)** を先行 — `tools/agentops_monitor/__main__.py` の notify CLI 拡張 + tests
   - argparse: `--kind` / `--message` / `--priority` / 既存 `--projects` `--project` `--dry-run` `--timeout` を維持
   - webhook resolver: `kind → envvar` 固定マッピング
   - payload builder: kind 別 embed format (allowed_mentions parse [] 必須)
   - rate-limit guard: ANT_TIME 系 kind に 1 分 5 / 1 時間 60 のホスト local state ガード
   - HTTP hardening: 429 / 5xx 受領時 exit 2 + `Retry-After` を state に記録
   - 旧 envvar `AGENTOPS_DISCORD_WEBHOOK_URL` deprecation 警告 (kind 未指定での後方互換 path に絞る)
   - 単体テスト追加 (`tools/agentops_monitor/tests/`): payload builder / resolver / rate-limit / 429 ハンドリング (urlopen を mock)
2. task 01 ローカル検証 → archive 移動 → commit → push → PR-A 作成 → cross-review (Codex) 依頼
3. PR-A マージ → main 同期 → **task 02 (PR-B)** で docs/11 実装ステータス注記更新 + cron / hook サンプル雛形

## 想定時間

- task 01 実装: 120 分
- task 01 テスト: 60 分
- task 01 cross-review + 反映: 45 分
- task 02 docs: 30 分
- task 02 cross-review + 反映: 30 分

## branch / PR

- task 01: `claude/agentops-monitor-kind-impl-2026-04-29` (現ブランチ)
- task 02: 同ブランチを継続 or 別ブランチ判断は task 01 マージ後

## 検証コマンド

```sh
# 構文チェック
python3 -m compileall tools/

# 単体テスト
python3 -m unittest discover tools/agentops_monitor/tests -v

# dry-run smoke
python3 scripts/agentops-watch notify --kind daily --projects config/projects.yml --dry-run
python3 scripts/agentops-watch notify --kind alert --message "smoke test" --dry-run
python3 scripts/agentops-watch notify --kind session-start --project /home/otaku/agentops --dry-run
python3 scripts/agentops-watch notify --kind permission-wait --project /home/otaku/agentops --message "Bash" --dry-run
python3 scripts/agentops-watch notify --kind stop-failure --project /home/otaku/agentops --message "test failure" --dry-run

# 旧 envvar 残存確認
grep -rn "AGENTOPS_DISCORD_WEBHOOK_URL" tools/ docs/ scripts/ rules/ skills/ workflows/ templates/ config/ 2>/dev/null

# markdown-link-check
npx markdown-link-check docs/11-monitoring-cli.md docs/18-notification-strategy.md

# cross-review
scripts/agentops delegate --to codex --role review_frontier --effort high --input tools/agentops_monitor/__main__.py
```

## 機微情報の取り扱い

- 単体テストでは webhook URL に **常に dummy 値** (`https://discord.invalid/webhooks/0/dummy` など) を使う
- 環境変数を一時的に設定するテストでは `unittest.mock.patch.dict(os.environ, ...)` を用い、テスト後に元へ戻す
- ユーザー実環境 envvar の値 (`echo $DISCORD_WEBHOOK_URL_*` 等) を **絶対に取得しない / 表示しない / log に出さない**
- `--dry-run` 出力には webhook URL を含めない (現行実装と同じ方針を維持)

## 完了基準 (task 01 + 02 共通)

- 上記検証コマンドが全て exit 0
- Codex cross-review P0/P1 0 件
- secret 混入なし
- archive 移動 + commit + push + PR + AI auto-merge 許諾条件評価まで完了
