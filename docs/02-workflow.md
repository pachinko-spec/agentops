# ワークフロー

## 標準サイクル

1. ブランチ確認
2. 調査
3. 設計
4. 設計レビュー
5. 実装
6. テスト
7. ドキュメント更新
8. commit
9. push
10. PR作成
11. レビュー
12. 修正
13. マージ
14. mainへ戻る
15. リモート反映と同期確認
16. マージ後報告

長時間の委譲、再現が必要なバグ修正、UI/外部CLI/MCPを使う検証、モデルやpromptの退行確認では、調査後に harness spec を作る。小さな修正では既存の DbC とテスト条件で足りる。詳細は [Harness Engineering](12-harness-engineering.md) を参照する。

## ブランチ運用

- 作業前に必ず現在ブランチを確認する。
- `main` / `master` / `develop` など保護対象ブランチへ直接commit/pushしない。
- 作業前に必ず作業ブランチを切る。
- Codexの作業ブランチは原則 `codex/` プレフィックスを使う。
- Claude Codeの作業ブランチは原則 `claude/` プレフィックスを使う。
- 既存プロジェクトにブランチ命名規則がある場合はプロジェクト側を優先する。
- マージ完了後は、必ず `main` ブランチに戻る。
- ローカルでマージした場合は、必ず `git push origin main` などでリモートへ反映する。
- マージ完了は、リモート反映後に `git status --short --branch` で `main...origin/main` が同期していることを確認した時点とする。

## マージ後報告

マージ完了後は、必ず次をユーザーへ提示する。

- 行った作業の要約
- 次セッション用プロンプト
- 次セッションで行うことの要約

次セッションで行うタスク、フェーズ、ステップがない場合は、「次タスクなし」と明記する。
ただし「次タスクなし」と書けるのは、リモート反映、同期確認、検証、ドキュメント更新、未解決リスク確認が完了している場合だけにする。運用反映、実環境導入、実モデルID確認、定期監視設定などが残る場合は、実装が完了していても次タスクとして明記する。

## セッション分割条件

次のいずれかに該当した場合、1セッションで完了させず、引き継ぎを作成する。

- 変更範囲が当初設計を超えた
- レビュー修正が2周を超える
- テスト失敗の自己修正が2周を超える
- 設計上の未解決事項が出た
- 次の作業者が必要な文脈を短く渡せなくなった

## ハンドオフ

セッションをまたぐ場合は、次を `.agentops/handoffs/` または `.agentops/prompts/` に残す。

- 今回完了したこと
- 未完了のこと
- 現在のブランチ
- 変更ファイル
- 実行したテスト
- 未解決リスク
- 次セッションへ投入するプロンプト

## クロスモデル委譲

Claude Code と Codex は、相互にCLI Wrapper経由で別モデルをサブエージェントとして使う。

```text
agentops delegate --to codex --role review_frontier --model <codex-model-id> --effort xhigh --input .agentops/plans/current.md
agentops delegate --to claude --role architect_frontier --model <claude-model-id> --effort xhigh --input .agentops/plans/current.md
```

委譲結果は `.agentops/runs/{run_id}/` に保存する。

```text
.agentops/runs/{run_id}/
  request.md
  status.json
  stdout.log
  result.md
  artifacts/
```

必要な場合は、委譲依頼の `request.md` に `.agentops/harnesses/<task>.yml` などの harness spec パスを明記する。
