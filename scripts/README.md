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
scripts/agentops-watch notify --dry-run --projects config/projects.yml
```

Discord webhook URL は `AGENTOPS_DISCORD_WEBHOOK_URL` で渡し、リポジトリには保存しません。
