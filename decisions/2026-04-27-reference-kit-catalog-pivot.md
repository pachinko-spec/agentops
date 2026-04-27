# reference kit catalog pivot

date: 2026-04-27
status: approved

## 背景

agentops は Claude Code / Codex のグローバル設定を見直すための参照キットとして整理してきた。一方で、`rules/`、`skills/`、`workflows/` に具体的なルール、Skill、手順の実体が大量に置かれていると、グローバル設定を行う AI エージェントがそれらをそのままコピーすべき完成品として誤解しやすい。

Claude Code と Codex では、グローバル指示、Skill、subagent、hook、permission、workflow の仕様と推奨される書き方が異なる。特に Skill の `name`、`description`、起動条件、tool 権限、配置場所は公式 docs と対象環境の現在仕様に合わせる必要がある。

## 決定

`rules/`、`skills/`、`workflows/` は完成済み設定ファイル群ではなく、AI エージェントがユーザーの開発方針、公式 docs、実環境、既存グローバル設定を確認したうえで生成するための候補カタログに転換する。

実際に Claude Code / Codex へ置く設定、Skill、subagent、workflow は、`templates/claude/`、`templates/codex/`、`templates/agentops/` の雛形と公式 docs を入力として、対象 CLI のエージェントが採否、命名、description、配置、tool 権限、検証方法を決める。

既存の具体 `rules/`、`skills/`、`workflows/` 実体は削除せず、`archive/reference-kit-v1/` へ退避する。これにより、過去の詳細な見本は参照可能なまま、現役入口は「候補一覧と生成方針」に集中できる。

## 採用する構造

- `rules/`: グローバル指示やプロジェクト指示へ採用しうる rule 候補のカタログ。
- `skills/`: 汎用性の高い Skill 候補の名前、用途、発火条件、global/project 向きのカタログ。
- `workflows/`: AI エージェントに生成させる workflow 候補のカタログ。
- `templates/claude/`: Claude Code 向けの CLAUDE.md、Skill、subagent、`.agentops` 利用サンプルの雛形。
- `templates/codex/`: Codex 向けの AGENTS.md、Skill、subagent、`.agentops` 利用サンプルの雛形。
- `templates/agentops/`: plan、task-plan、task、next-session prompt のサンプル。
- `archive/reference-kit-v1/`: 旧 `rules/`、`skills/`、`workflows/` 実体の退避先。

## 採用しないこと

- `rules/`、`skills/`、`workflows/` に置かれた具体ファイルを、そのままグローバル設定へ機械的にコピーする運用。
- Claude Code / Codex の仕様差を無視した共通 Skill 実体を正として配布する運用。
- `.agentops/archive/` に参照キット本体の旧実体を混ぜる運用。

## 影響範囲

- README の位置づけ。
- `docs/15-reference-kit-structure.md` の分類案。
- `docs/16-global-settings-application-checklist.md` の反映手順。
- `config/claude/CLAUDE.md` と `config/codex/AGENTS.md` の参照表現。
- `config/understand-anything-policy.json` の対象 glob。
- `rules/`、`skills/`、`workflows/` の実体配置。
- 新設する `templates/` と repo 直下 `archive/`。

## 検証方針

- README、docs、config、templates、archive からの参照が新構造に合っていることを `rg` で確認する。
- `git diff --check`
- `scripts/agentops-watch check --projects config/projects.yml`
