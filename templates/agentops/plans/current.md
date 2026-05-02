# Plan: <plan title>

plan-id: <yyyy-mm-dd-slug>
status: approved
created_at: <yyyy-mm-dd>
timezone: Asia/Tokyo

## 背景

なぜこの plan が必要かを書く。

## 目的

- 達成したいこと。

## 非目的

- 今回やらないこと。

## 影響範囲

- 変更対象。

## Phase 構造

| # | Phase | work area | 担当 |
|---|---|---|---|
| 1 | 設計 / 影響範囲調査 | plan / task | Claude orchestrator_frontier |
| 1.5 | Phase ownership lint | plan / task | 軽量モデル docs_agent / coding_fast / research_fast |
| 2 | 設計レビュー | plan | Codex review_frontier (effort high) |
| 3 | 実装 | repository files | Codex coding_frontier (effort high) |
| 4 | 実装レビュー | diff | Codex review_frontier (effort high) |
| 5 | 最終判断 | diff + verification | Claude orchestrator |

## Phase 着手記録

- Phase X — 担当: <model or CLI> (<role>)

## 完了条件

- 完了と判断できる条件。

## 停止条件

- ユーザー確認や分割が必要になる条件。

## 検証方針

- 実行する検証コマンドや確認項目。
