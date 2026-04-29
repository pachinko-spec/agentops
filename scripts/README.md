# scripts

cron、hooks、CLI Wrapperの入口となるスクリプトを置く場所です。

## 実装済み

- `agentops`
- `agentops-watch`
- `check-protected-branch`
- `check-tests-before-push`
- `install-hooks`
- `hooks/pre-commit`
- `hooks/pre-push`

## 例

```sh
scripts/install-hooks --target . --mode copy
scripts/agentops delegate --to codex --role review_frontier --dry-run --input README.md
scripts/agentops-watch check --projects config/projects.yml
# 現行実装 (--kind 未対応)
scripts/agentops-watch notify --dry-run --projects config/projects.yml

# 契約 (将来実装、別 plan で追加。詳細は [docs/11](../docs/11-monitoring-cli.md) と [docs/18](../docs/18-notification-strategy.md))
scripts/agentops-watch notify --kind daily --dry-run --projects config/projects.yml
```

Discord webhook URL は kind 別に `DISCORD_WEBHOOK_URL_{DAILLY,WEEKLY,MONTHLY,ANT_TIME}` で渡し、リポジトリには保存しません。channel 区分と SECRET 管理は [docs/18-notification-strategy.md](../docs/18-notification-strategy.md) を参照してください。旧 `AGENTOPS_DISCORD_WEBHOOK_URL` は deprecated です。
