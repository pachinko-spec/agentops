# ワークフロー

## 実装前の計画と承認

実装、削除、ファイル生成、インストール、外部反映の前に、必ず計画をユーザーへ提示し、承認を得る。

承認を省略できるのは、承認済みの同一plan内でセッション跨ぎの別フェーズまたは別taskを継続する場合のみである。ただし、その場合でも今回セッションで行う小分け計画とtaskは必ず明示する。

`.agentops` では次の責務に分ける。

- `.agentops/plans/current.md`: 大きい承認済みplan。原則最大1つ。
- `.agentops/task-plans/current.md`: 今回セッションまたは復帰用の実行計画。
- `.agentops/tasks/*.md`: 未完了、進行中、blockedの子task。
- `.agentops/archive/<plan-id>/`: 完了、中止、置き換え済みのplan/task/task-plan。


## 標準サイクル

1. ブランチ確認
2. 調査
3. 計画提示とユーザー承認
4. task-planとtasks作成
5. 設計
6. 設計レビュー
7. 実装
8. テスト
9. ドキュメント更新
10. 自己レビュー
11. commit
12. push
13. PR作成
14. レビュー
15. 修正
16. 最終レビュー
17. GitHub上でPRをマージ
18. mainへ戻る
19. remote main取得と同期確認
20. 完了済みtaskとplanをarchiveへ移動
21. マージ後報告

長時間の委譲、再現が必要なバグ修正、UI/外部CLI/MCPを使う検証、モデルやpromptの退行確認では、調査後に harness spec を作る。小さな修正では既存の DbC とテスト条件で足りる。詳細は [Harness Engineering](12-harness-engineering.md) を参照する。

レビュー後に修正した場合は、必ず再レビューを行う。標準サイクルは修正で終わらせず、最終レビューで未解決の P0/P1 と意図しない差分がないことを確認してから次工程へ進む。

## ブランチ運用

- 作業前に必ず現在ブランチを確認する。
- バージョン管理は必ず GitHub を正とする。GitHub remote または PR 運用が使えない場合は、ローカル作業だけで完了扱いしない。
- `main` / `master` / `develop` など保護対象ブランチへ直接commit/pushしない。
- 作業前に必ず作業ブランチを切る。
- Codexの作業ブランチは原則 `codex/` プレフィックスを使う。
- Claude Codeの作業ブランチは原則 `claude/` プレフィックスを使う。
- 既存プロジェクトにブランチ命名規則がある場合はプロジェクト側を優先する。
- commit 後は作業ブランチをリモートへ push し、GitHub 上で PR を作成する。
- レビューとマージ判断は PR 上に残す。ローカルで main へマージして完了扱いしない。
- マージは GitHub 上の PR で行う。例外的にローカルマージが必要な場合は、事前にユーザーへ確認し、理由を PR または handoff に残す。
- マージ完了後は、必ず `main` ブランチに戻り、remote の `main` を取得する。
- マージ完了は、`git status --short --branch` で `main...origin/main` が同期し、PR が merged 状態になっていることを確認した時点とする。

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
