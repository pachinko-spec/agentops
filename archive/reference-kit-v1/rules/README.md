# rules

AIエージェントが常時適用する判断基準を置く場所です。

`rules/` は実行時の正本です。背景、理由、設計思想は `docs/` に置きます。Claude Code や Codex の実設定へは `config/` から投影します。

## 一覧

- `planning-approval.md`: 実装前の計画提示、承認、小分けtask-plan。
- `project-template-scope.md`: 実プロジェクトへ持ち出すテンプレートの対象範囲。
- `deployment-target-policy.md`: Cloudflare / Xserver / GCP / ローカルサーバーの選定方針。
- `dry-principle.md`: DRY原則と正本の分離。
- `source-of-truth.md`: `rules/`、`skills/`、`workflows/`、`docs/`、`config/` の責務。
- `language-policy.md`: 日本語運用と英語を残す条件。
- `review-policy.md`: レビューの基本姿勢。
- `design-policy.md`: 設計時の基本観点。
- `git-and-branch-policy.md`: GitHub、branch、PR、mergeの運用。
- `documentation-policy.md`: ドキュメント更新の完了条件。
- `freshness-policy.md`: 公式docs、LTS、release notes確認。
