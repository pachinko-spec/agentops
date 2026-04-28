# DEPRECATED — reference kit v1

> 廃止日: 2026-04-27
> 状態: 廃止（archive 退避済み、削除しない）
> 後継: [rules/catalog.md](../../rules/catalog.md) / [skills/catalog.md](../../skills/catalog.md) / [workflows/catalog.md](../../workflows/catalog.md)
> 出典: [decisions/2026-04-27-reference-kit-catalog-pivot.md](../../decisions/2026-04-27-reference-kit-catalog-pivot.md)

## 概要

`archive/reference-kit-v1/` は、agentops が「`rules/` / `skills/` / `workflows/` に具体実体を置く完成品集」から「候補カタログ + 各 CLI のエージェントによる生成方針」へ pivot した際に退避された旧構造です。

退避理由と経緯の詳細は同階層の [README.md](README.md) および [decisions/2026-04-27-reference-kit-catalog-pivot.md](../../decisions/2026-04-27-reference-kit-catalog-pivot.md) を参照してください。本ファイルは機械可読な廃止メタデータ（廃止日・後継入口・再有効化条件）を提供する目的に絞っています。

## 現役入口

新規で rule / skill / workflow を参照したい場合は、本ディレクトリではなく以下を読んでください。

- rule 候補: [rules/catalog.md](../../rules/catalog.md)
- skill 候補: [skills/catalog.md](../../skills/catalog.md)
- workflow 候補: [workflows/catalog.md](../../workflows/catalog.md)
- グローバル設定反映チェックリスト: [docs/16-global-settings-application-checklist.md](../../docs/16-global-settings-application-checklist.md)

`templates/claude/` / `templates/codex/` / `templates/agentops/` の雛形と公式 docs を入力に、対象 CLI のエージェントが採否・命名・配置・tool 権限を判断する設計です。`archive/reference-kit-v1/` 配下のファイルを直接グローバル設定へコピーしないでください。

## 再有効化条件

本ディレクトリは再有効化しません。

過去の見本コンテンツが新たに必要になった場合は、現役 `rules/` / `skills/` / `workflows/` に新規エントリとして再起票してください。`archive/` 配下は参照可能な状態を保ったまま変更・移動しない方針です（`README.md` 先頭への DEPRECATED 注記行追加など、退避済みであることの明示は許容）。

## 想定読者

- 過去 commit や検索経由で本ディレクトリにたどり着いた人
- 旧 `rules/<id>.md` / 旧 `skills/<area>/SKILL.md` / 旧 `workflows/<id>.md` を引用している外部資料を更新する人

## 構造

- `rules/`: 旧 rule 実体（個別 Markdown）
- `skills/`: 旧 SKILL.md 群（`design/` / `docs/` / `implementation/` / `ops/` / `review/`）
- `workflows/`: 旧 workflow 実体（個別 Markdown）

各サブディレクトリの `README.md` 先頭にも DEPRECATED 注記があります。配下の個別 Markdown ファイル本文には注記を入れていません（README.md の注記から辿れます）。
