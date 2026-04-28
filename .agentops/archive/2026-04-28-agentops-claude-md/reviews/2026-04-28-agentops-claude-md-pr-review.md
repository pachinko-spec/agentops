# 2026-04-28 agentops project CLAUDE.md PR review

## 対象

- PR: https://github.com/pachinko-spec/agentops/pull/24
- ブランチ: `claude/agentops-claude-md`
- 変更ファイル:
  - 新規: `/home/otaku/agentops/CLAUDE.md` (47行)
  - 修正: `/home/otaku/agentops/README.md` (2箇所、3行差分)

## 実施者

- `agentops-reviewer` subagent (Claude Code 内の独立レビュー)

## 観点

1. AGENTS.md との章立て対応 (位置づけ／記録先／`~/.claude` を触る作業／Git／完了／停止 の 6章)。
2. Codex 用語と Claude Code 用語の翻案精度 (意図しない `codex` / `~/.codex` / `config.toml` / `codex/` ブランチ残留がないか)。
3. Claude Code 機能名 (`settings.json`、`skills/`、`agents/`、`plugins/`、hooks、MCP、permission、`/memory` `/config` `/mcp`) の正しさ、`config/claude/CLAUDE.md` (131行雛形) との整合。
4. `docs/07-global-vs-project.md`、`docs/08-config-templates.md`、`docs/15-reference-kit-structure.md`、`docs/16-global-settings-application-checklist.md` との内容整合。
5. secret / token / 固定 model id の混入がないか。
6. README フォルダ構成図のアラインメント。

## 結果

- P0: なし。
- P1: なし。
- P2: 2件 (いずれもスコープ外として次セッション課題化、本 PR では修正不要)
  - AGENTS.md 側にも CLAUDE.md への対称クロスリファレンスを入れるべき (今回スコープでは AGENTS.md は触らない方針)。
  - `subagent` と `agents/` (置き場名) の本文注記を入れると親切 (任意)。
- P3: なし。

## マージ可否判断

- マージ可。P0 / P1 がゼロ、P2 はスコープ外として延期可、再レビュー不要。

## 検証

- 章タイトル対応: 6章すべて AGENTS.md / CLAUDE.md で対応。
- Codex 残留: 5行目 (クロスリファレンス) と 9行目 (リポジトリ説明) のみ、いずれも意図的。
- Claude Code 用語: `config/claude/CLAUDE.md` (52, 54, 56-58行)、`docs/08-config-templates.md` (45-52行)、`docs/16-global-settings-application-checklist.md` と整合。
- secret / token / 固定 model id の混入なし。
- README 95-99行のフォルダ構成図、新規 `|-- CLAUDE.md` 行は AGENTS.md 行と 4スペース揃えで一致、桁揃え破綻なし。

## 残リスク

- 静的レビューでは「Claude Code がこのリポジトリ直下の CLAUDE.md を起動時に実際にロードするか」までは検証できない。マージ後、`/home/otaku/agentops` で Claude Code を起動し `/memory` 相当の確認方法でプロジェクト指示として読み込まれることを確認することを推奨。
- AGENTS.md 側への対称クロスリファレンス追記は P2 として別 PR / 次セッション課題化。
