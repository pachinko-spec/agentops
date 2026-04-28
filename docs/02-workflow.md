# ワークフロー

## 実装前の計画と承認

実装、削除、ファイル生成、インストール、外部反映の前に、必ず計画をユーザーへ提示し、承認を得る。

承認を省略できるのは、承認済みの同一plan内でセッション跨ぎの別フェーズまたは別taskを継続する場合のみである。ただし、その場合でも今回セッションで行う小分け計画とtaskは必ず明示する。

ユーザーの指示が曖昧、断片的、または急なアイデアを含む場合は、思い込みで実装に進まない。不明点、懸念点、代替提案、ユーザー判断が必要なリスクを整理し、計画に含めて確認する。

`.agentops` では次の責務に分ける。

| パス | 役割 | 解像度 |
|---|---|---|
| `.agentops/plans/current.md` | 承認済みの大きいplan（原則最大1つ、親task一覧必須） | 計画全体 |
| `.agentops/task-plans/current.md` | 今回セッション実行計画（親plan・フェーズ・時間予測） | セッション |
| `.agentops/tasks/*.md` | plan内の作業単位（PR単位など）。新作業は次番号ファイルに追記。完了済みは `.agentops/archive/<plan-id>/tasks/` へ移す | 中 |
| `.agentops/reviews/` | レビュー結果（P0/P1/P2/P3 分類） | 各レビュー |
| `.agentops/runs/` | cross-model 委譲の実行記録（ISO8601 timestamp + CLI 名） | 各実行 |
| `.agentops/handoffs/` | **planで考えたtaskの範囲を超えた持ち越しのみ**（別planへの申し送り、長期 blocker、計画外で発生した観察事項など）。PR単位の進捗には使わない | planを跨ぐ |
| `.agentops/prompts/next-session.md` | 次セッション投入プロンプト。動的に参照先を決める: `tasks/` に未完了があればtasksベース、なければ `handoffs/` ベース、両方なければ生成しない（既存ファイルがあれば削除） | エントリポイント |
| `.agentops/archive/<plan-id>/` | 完了、中止、置き換え済みのplan/task-plan/task/reviews/handoffs。`archive/README.md` を完了plan時系列インデックスとして運用 | plan単位 |


## 標準サイクル

以下の 24 ステップは reference であり、すべてを毎回実行する必要はない。[設計思想](01-philosophy.md) の中核原則「単純で合成可能な workflow を優先する」に従い、対象作業の規模・リスク・再現要件に応じて取捨選択する。小さな typo 修正や docs 行の誤字訂正は調査 + 計画 + 実装 + commit + PR で十分なことが多く、harness spec や cross-review が不要な場合もある。

1. 対象プロジェクト確認。実プロジェクトでは `~/dev` 配下、dotfiles除外、プロジェクト固有設定優先を確認する。
2. ブランチ確認
3. 調査
4. 不明点、懸念点、代替案、エスカレーション要否を整理する。
5. 計画提示とユーザー承認
6. **実装着手前**に `.agentops/plans/current.md`、`.agentops/task-plans/current.md`、`.agentops/tasks/*.md` を生成する
7. 設計
8. 設計レビュー
9. 実装
10. テスト
11. ドキュメント更新
12. 自己レビュー
13. release readiness確認。外部公開や本番反映がある場合はrollbackと監視も確認する。
14. **commit前**に `.agentops/` を整える
    - 14a. 完了済み task と `plans/current.md`、`task-plans/current.md` を `.agentops/archive/<plan-id>/` へ移動する
    - 14b. 完了 handoff は `archive/<plan-id>/handoffs/` へ移し、`handoffs/` 直下は進行中のみ残す
    - 14c. `archive/README.md` 時系列インデックスに今回 plan-id 行を追加する
15. commit
16. push
17. PR作成
18. レビュー
19. 修正
20. 最終レビュー
21. GitHub上でPRをマージ
22. mainへ戻る
23. remote main取得と同期確認
24. マージ後報告

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

次のいずれかに該当した場合、1セッションで完了させず、ハンドオフを作成する。

- 変更範囲が当初設計を超えた
- レビュー修正が2周を超える
- テスト失敗の自己修正が2周を超える
- 設計上の未解決事項が出た
- 次の作業者が必要な文脈を短く渡せなくなった

## ハンドオフ

セッションをまたぐ場合は、状況に応じて以下を残す。

- 進行中・blocked の作業は `.agentops/tasks/*.md` を最新化する。これが次セッションの入口になる。
- planで考えたtaskの範囲を超えた持ち越し（別planへの申し送り、長期 blocker、計画外で発生した観察事項など）は `.agentops/handoffs/` に残す。**PR単位の進捗には使わない**。
- 次セッション投入プロンプトは `.agentops/prompts/next-session.md` に置く。参照先は動的に決める: `tasks/` に未完了があればtasksベース、なければ `handoffs/` ベース、両方なければ生成しない（既存ファイルがあれば削除する）。

`handoffs/` または `prompts/next-session.md` に残す場合の必須項目:

- 今回完了したこと
- 未完了のこと
- 現在のブランチ
- 変更ファイル
- 実行したテスト
- 未解決リスク
- 次セッションへ投入するプロンプト

完了 handoff は対応する `.agentops/archive/<plan-id>/handoffs/` へ移し、`handoffs/` 直下は進行中のハンドオフだけにする。

## cross-model 委譲

Claude Code と Codex は、相互に CLI Wrapper 経由で別モデルをサブエージェントとして使う。

cross-review / cross-model review は、特定モデルを固定する運用ではない。現在の主 orchestrator とは別系列、別 CLI、別モデルファミリーの frontier reviewer を入れ、同じ設計や差分を別の推論系で確認するための思想である。Codex 主体なら Claude Code / Anthropic 系、Claude Code 主体なら Codex / OpenAI 系が候補になりうる。実際の model id は、対象 CLI の現在仕様と公式 docs を確認してから指定する。

cross-review は高リスク設計だけに限定しない。新規機能追加、リファクタリング、依存追加、API 契約変更、デプロイ影響、レビュー指摘の修正後にも検討する。ただし全変更で必須にはせず、影響範囲、コスト、レイテンシ、既存検証の強さを見てオーケストレーターが採否を判断する。

委譲先 reviewer は所見を出す。採否、修正範囲、延期、停止、統合判断は主 orchestrator が持つ。

```text
agentops delegate --to codex --role review_frontier --model <codex-model-id> --effort xhigh --input .agentops/plans/current.md
agentops delegate --to claude --role review_frontier --model <claude-model-id> --effort xhigh --input .agentops/plans/current.md
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
