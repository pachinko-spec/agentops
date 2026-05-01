---
last_reviewed: 2026-04-28
next_review_by: 2026-07-31
reviewer: pachinko-spec
language: ja
applies-to: global
---

# DbCと品質ゲート

## DbCテンプレート

各タスクは次を明示する。

DbC はすべてのタスクに使う軽量な契約である。再現性、artifact、oracle、sandbox 条件まで必要な作業では、DbC を task spec と実行条件へ展開した harness spec を使う。詳細は [Harness Engineering](12-harness-engineering.md) を参照する。

```md
## 前提条件
- 触ってよい範囲
- 依存関係
- 事前に確認すべき仕様

## 不変条件
- 壊してはいけない互換性
- 既存テストで守るべき挙動
- セキュリティ・認可・データ保護の条件

## 完了条件
- 実装完了
- 必要なテストが成功
- ドキュメント更新済み
- PR本文に検証結果を記載
- GitHub上にPR、レビュー、マージ履歴が残っている

## 禁止事項
- main直push
- ローカル main への merge だけで完了扱いすること
- 無断の破壊的コマンド
- スコープ外リファクタ
- 無限Issue起票

## 停止条件

### プロセス層（人間判断・ループ防止）

- テスト失敗修正が2周を超えた
- レビュー修正が2周を超えた
- 仕様判断が必要になった
- セキュリティ・データ損失リスクが出た

### tool 実行層（個別ツール呼び出しの暴走防止）

- max_tool_calls 超過（既定 200 回）
- no_progress_steps 超過（既定 10 ステップ進捗無し）
- circuit_breaker_cycle_threshold 超過（同一サイクル 3 回検知）
- cost_cap_usd_per_session 超過（既定 USD 20 / session）

これらの閾値は `config/harness.yml` の `defaults.stop_conditions.tool_layer` に機械可読 spec として保持する。プロジェクトごとに上書きできる。閾値の根拠は runaway agent の代表事例（cordum.io / blog.meganova.ai）と ABC 論文 (arXiv:2602.22302) の (p, δ, k)-satisfaction を参考にしているが、具体額は固定しない（一次性が弱いため）。
```

## commit / push条件

- テスト未実行ならcommit/pushしない。
- テスト失敗状態ではcommit/pushしない。
- 例外が必要な場合はユーザーに確認し、commit messageまたはPR本文に理由を書く。

このリポジトリでは、実装雛形として次を提供する。

- `scripts/check-protected-branch`
- `scripts/check-tests-before-push`
- `scripts/hooks/pre-commit`
- `scripts/hooks/pre-push`
- `scripts/install-hooks`

詳細は [hooks品質ゲート](09-hooks-quality-gates.md) を参照する。

## PR条件

- PR本文に実施内容、検証結果、未解決リスクを書く。
- 関連docsを更新する。
- レビュー指摘の対応方針を明示する。

## マージ条件

- CIが通っている
- 必須レビューが通っている
- P0/P1指摘が残っていない
- mainへ直接pushしていない
- ユーザーまたはルール上許可されたAIがマージしてよい状態
- GitHub上のPRでマージし、ローカル main と origin/main が同期している
- post-merge 整理を別 chore PR に分離していない (詳細は次節 §post-merge 手順)

## post-merge 手順 (1 PR scope 完結原則)

merge 対象 PR が要求する以下の整理作業は、**merge 前 commit に含める** ことを原則とする (1 PR scope 完結原則):

- 完了 task の `.agentops/archive/<plan-id>/tasks/` 移動
- `plans/current.md` の進捗反映 / 完了マーカー更新
- `task-plans/current.md` の archive (plan 完了時) または更新
- `prompts/next-session.md` の次セッション entry 反映

merge 完了直後の必須手順 (post-merge):

1. `git checkout main && git fetch origin && git pull --ff-only origin main` で同期確認
2. `agentops repo` では `scripts/agentops archive task --task-id <basename>` を **merge 前 commit** で実行済みであることを `ls .agentops/archive/<plan-id>/tasks/` で read-only 確認 (本コマンドは entry_point と completed_tasks を一括更新)
3. `git status --short` で merge 後 dirty diff が無いこと確認
4. plan 全体完了時のみ、merge 前 commit で `scripts/agentops archive plan --plan-id <id> --summary <text>` 実行済みであることを `archive/README.md` で確認

**例外**: 上記整理を別 chore PR に分離する運用は **user 明示許可がある場合のみ** 許容する。理由は run log / handoff / 元 PR 本文に残す。詳細な「user 明示許可」3 要件は `~/.claude/rules/auto-merge-permission.md` § auto-merge 後の必須手順を参照。

詳細は rules: `auto-merge-permission.md` § auto-merge 後の必須手順、`session-record-and-handoff.md` § prompts/next-session.md の同セッション内更新原則。関連 workflow は `docs/02-workflow.md` を参照。
