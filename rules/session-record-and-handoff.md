---
name: session-record-and-handoff
description: `.agentops/` 配下の plans / task-plans / tasks / reviews / runs / handoffs / prompts / archive の責務、運用フロー、セッション分割条件、マージ後報告、prompts/next-session.md の同セッション内更新原則。
applies-to: global
---

# セッション記録と継続

`.agentops/` 配下に作業ログを残す。作業の長短や 1 セッション完結かどうかに関係なく、プロジェクトルート直下 (`./.agentops/`) または `~/.claude` を触るグローバル作業 (`~/.claude/.agentops/`) では、以下を運用する。プロジェクト固有の `.agentops/` がある場合はそちらを優先する。

## ファイル種別と責務

| パス | 役割 | 解像度 |
|---|---|---|
| `plans/current.md` | 承認済みの大きい plan（最大 1 つ、親 task 一覧必須） | 計画全体 |
| `task-plans/current.md` | 今回セッション実行計画（親 plan・フェーズ・時間予測） | セッション |
| `tasks/*.md` | plan 内の作業単位（PR 単位など）。新作業は次番号ファイルに追記。完了済みは `archive/<plan-id>/tasks/` へ移す | 中 |
| `reviews/` | レビュー結果（P0/P1/P2/P3 分類） | 各レビュー |
| `runs/` | クロスモデル委譲の実行記録（ISO8601 timestamp + CLI 名） | 各実行 |
| `handoffs/` | **plan で考えた task の範囲を超えた持ち越し** のみ（別 plan への申し送り、長期 blocker、計画外で発生した観察事項など）。PR 単位の進捗には使わない | plan を跨ぐ |
| `prompts/next-session.md` | 次セッション投入プロンプト。動的に参照先を決める: `tasks/` に未完了があれば tasks ベース、なければ `handoffs/` ベース、両方なければ削除 | エントリポイント |
| `archive/<plan-id>/` | 完了・中止・置き換え済みの plan / task / task-plan / reviews / handoffs。`archive/README.md` を完了 plan 時系列インデックスとして運用 | plan 単位 |

## 運用フロー（プロジェクト直下・`~/.claude` グローバル共通）

1. 計画を提示し、ユーザー承認を得る。
2. 承認後、**実装に着手する前**に対象の `.agentops/plans/current.md` と `task-plans/current.md`、必要な `tasks/*.md` を生成する。新たな操作を入れる場合は `tasks/` の次番号ファイルに追加する。
3. 実装、検証、レビューを行う。レビュー結果は `reviews/` に残す。
4. **commit する前**（git 管理外の場合は実装完了直後）に、完了 task と `plans/current.md`、`task-plans/current.md` を `archive/<plan-id>/` 配下へ移す。完了済み task を未完了入口に残さない。
5. （リポジトリ管理対象なら）commit / push / PR / マージ / main 同期確認まで進める。

## 完了 handoff の扱い

- `handoffs/` 直下は **進行中の引き継ぎだけ** にする。完了した plan に紐づく handoff は `archive/<plan-id>/handoffs/` へ移す。
- `archive/README.md` を「完了 plan 時系列インデックス」として運用し、完了日 / plan-id / サマリを新しい順で列挙する。各 plan の詳細は `archive/<plan-id>/plan.md` から辿る。

## セッション跨ぎ

- 1 セッションで終わらない場合、進行中 task が残っているなら `tasks/*.md` を最新化し、`prompts/next-session.md` で次番号 task を指す。
- plan の task 範囲を超えた持ち越し（別 plan への申し送り、長期 blocker、計画外観察事項など）があれば `handoffs/` に新規ファイルを残し、`prompts/next-session.md` で handoff を指す。
- 残作業がなければ `prompts/next-session.md` が残っていても **削除する**。

## prompts/next-session.md の同セッション内更新原則

`prompts/next-session.md` は **次セッション entry を常に指す状態** に保つ。セッション終了時点で内容が古い (前回セッションの完了 task を指している、または存在しない archive 済 task を指している等) ならば、本セッション内で更新する。

- post-merge 別 PR で更新する運用は **禁止** (1 PR scope 完結が原則)。
- hook 整合: `~/.claude/hooks/_common.py` (`inspect_agentops` 関数、`"before finalizing"` block message を emit する箇所) は Stop 時に completed task 残存を block する。これは「同セッション内整理」を意図する設計であり、`prompts/next-session.md` 更新もこの意図に従う。
- agentops repo では `scripts/agentops archive task --task-id <basename>` 実行で `entry_point` と `completed_tasks` が一括更新される。本コマンドは Phase 4.5 (merge 前 commit に含める) で実施し、merge 後は read-only 確認のみ。
- 例外: user 明示許可で別 chore PR 分離する場合のみ、本セッション内更新を見送る (`auto-merge-permission.md` § auto-merge 後の必須手順「user 明示許可」3 要件を参照)。

## セッション分割条件

次のいずれかに該当した場合、1 セッションで完了させずハンドオフを作成する。

- 変更範囲が当初設計を超えた
- レビュー修正が 2 周を超える
- テスト失敗の自己修正が 2 周を超える
- 設計上の未解決事項が出た
- 次の作業者が必要な文脈を短く渡せなくなった

ハンドオフ生成手順は skill `session-handoff` を使う。

## マージ後報告

マージ完了後はユーザーへ次を提示する。

- 行った作業の要約
- 次セッション用プロンプト
- 次セッションで行うことの要約

「次タスクなし」と書けるのは、リモート反映、同期確認、検証、ドキュメント更新、未解決リスク確認が完了している場合だけ。運用反映、実環境導入、実モデル ID 確認、定期監視設定などが残る場合は、実装が完了していても次タスクとして明記する。
