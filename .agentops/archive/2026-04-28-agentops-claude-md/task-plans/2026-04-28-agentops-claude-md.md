# 2026-04-28 agentops project CLAUDE.md

## 状態

- 完了。
- 作業ブランチ: `claude/agentops-claude-md`
- PR: https://github.com/pachinko-spec/agentops/pull/24

## 親 plan

- ローカル plan: `~/.claude/plans/claude-agentops-agents-md-claude-md-buzzing-quail.md`

## 前提条件

- 対象は `/home/otaku/agentops` リポジトリ内のプロジェクト指示と関連 docs。
- `~/.claude` の実設定ファイルは今回は直接変更しない。
- ルート `CLAUDE.md` は、このリポジトリで作業する Claude Code へのプロジェクト固有指示として扱う。
- 既存ルート `AGENTS.md` (Codex 向け 45行) と章立てを完全対応させる。
- グローバル `~/.claude/CLAUDE.md` (個人指示型・簡潔) はユーザー指示で今回触らない。
- `~/.codex/AGENTS.md` 実体との整合確認は今回スコープ外。

## 不変条件

- 機密値、認証情報、環境変数ファイル、個人情報を `.agentops/` や docs に残さない。
- `config/claude/CLAUDE.md` は `~/.claude/CLAUDE.md` 用の雛形であり、実設定と混同しない。
- `main` へ直接 commit / push しない。

## 実行内容

1. 作業ブランチ `claude/agentops-claude-md` を切る。
2. ルート `CLAUDE.md` を新規作成し、`AGENTS.md` の章構成 (位置づけ／記録先／`~/.claude` を触る作業／Git／完了／停止) を完全踏襲しつつ Codex 用語を Claude Code 用語へ翻案する。
3. README の「プロジェクト固有指示」記述とフォルダ構成図に `CLAUDE.md` を追記する。
4. 静的検証 (grep による Codex 残留チェック、章タイトル対応確認) を行う。
5. commit、push、GitHub PR 作成、independent reviewer による PR レビュー、GitHub 上でマージ、main 同期確認まで進める。

## 用語翻案ルール

| AGENTS.md (Codex 向け) | CLAUDE.md (Claude Code 向け) |
|---|---|
| `config/codex/AGENTS.md` | `config/claude/CLAUDE.md` |
| `~/.codex/AGENTS.md` | `~/.claude/CLAUDE.md` |
| `~/.codex/config.toml` | `~/.claude/settings.json` |
| `~/.codex/skills/` | `~/.claude/skills/` |
| `~/.codex/plugins/` | `~/.claude/plugins/` |
| `~/.codex` 配下 hooks / MCP / subagents | `~/.claude` 配下 hooks / MCP / `agents/` (subagent) / skills / permission |
| `~/.codex/.agentops/` | `~/.claude/.agentops/` |
| `codex --help` | `claude --help` および `claude --version` |
| `codex/` プレフィックス | `claude/` プレフィックス |

## 完了条件

- ルート `CLAUDE.md` の章タイトルが `AGENTS.md` と完全一致。
- Codex 用語がすべて Claude Code 用に翻案されている (意図的なクロスリファレンスとリポジトリ説明を除く)。
- README からプロジェクト固有指示 (Claude Code 向け) を見つけられる。
- `git diff` で意図しない差分がない。
- レビュー (P0 / P1 / P2 / P3 分類) で P0 / P1 がない。
- 作業の最後はレビュー結果の確認で終える。

## 検証結果

- ルート `CLAUDE.md` を作成した。AGENTS.md と章立て完全対応 (6章)。
- README の「プロジェクト固有指示」説明を Codex / Claude Code 両対応に書き換え、フォルダ構成図に `CLAUDE.md` 行を追加した。
- grep による静的検証で意図しない Codex 残留なし、Claude Code 用語が適切に登場。
- independent reviewer (`agentops-reviewer`) による PR レビュー: P0 / P1 / P2 / P3 すべて該当指摘なし、マージ可判断。レビュー詳細は `reviews/2026-04-28-agentops-claude-md-pr-review.md` 参照。
- 今回は `~/.claude` の実ファイルを変更していない。

## 停止条件

- `~/.claude` 実ファイルへの書き込みが必要になった場合。
- 機密値や個人情報を扱う必要が出た場合。
- AGENTS.md と CLAUDE.md の対称化を超えて改訂範囲が広がる場合。
- レビュー修正が 2 周を超えそうな場合。

## 残リスク・次セッション課題

- AGENTS.md 側に CLAUDE.md への対称クロスリファレンスを入れる (今回スコープ外、reviewer 指摘 P2)。
- `subagent` と `agents/` (置き場名) の本文注記を入れるか検討 (reviewer 指摘 P2、任意)。
- Claude Code 実グローバル設定 (`~/.claude/CLAUDE.md` 含む) への反映作業は別タスク。
- Codex 実グローバル設定 (`~/.codex/AGENTS.md`) と `config/codex/AGENTS.md` 雛形 (131行) との整合確認は別タスク。

## 変更ファイル

- 新規: `/home/otaku/agentops/CLAUDE.md`
- 修正: `/home/otaku/agentops/README.md` (2箇所)
- 新規: `/home/otaku/agentops/.agentops/archive/2026-04-28-agentops-claude-md/task-plans/2026-04-28-agentops-claude-md.md`
- 新規: `/home/otaku/agentops/.agentops/archive/2026-04-28-agentops-claude-md/reviews/2026-04-28-agentops-claude-md-pr-review.md`
