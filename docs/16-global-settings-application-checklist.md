# グローバル設定反映チェックリスト

## 目的

このチェックリストは、`agentops` の設計思想と雛形を Claude Code / Codex の実グローバル設定へ反映するときに使う。反映対象は `CLAUDE.md` / `AGENTS.md` だけではなく、settings、config、MCP、hooks、skills、subagents、permissions、sandbox、approval、shell profile、GitHub remote を含めて確認する。

このリポジトリの docs、rules、skills、workflows、templates、config は参照資料と反映候補であり、そのまま機械的にコピーしない。`rules/`、`skills/`、`workflows/` は候補カタログ、`templates/` は生成雛形として扱う。反映時点の公式 docs、CLI の `--help`、対象環境の実設定を確認して、採用する内容、調整する内容、見送る内容を計画する。

## 反映前

- [ ] 対象 CLI、バージョン、起動経路、実行場所を確認した。
- [ ] 対象 CLI の公式 docs と `--help` で、現在の設定ファイル、読み込み順、CLI 引数、MCP、hooks、skills、subagents、permission / sandbox / approval の扱いを確認した。
- [ ] 既存の `~/.claude/CLAUDE.md`、`~/.claude/settings.json`、`~/.codex/AGENTS.md`、`~/.codex/config.toml`、MCP 設定、shell profile、GitHub remote を読み、secret をログや PR に出さないようにした。
- [ ] プロジェクト固有の `CLAUDE.md` / `AGENTS.md` / docs / `.agentops/` がある場合は、グローバルより優先する前提を確認した。
- [ ] 反映対象、非対象、リスク、停止条件、検証方法をユーザーへ提示し、承認を得た。

## `CLAUDE.md` / `AGENTS.md` の書き方

- [ ] 安定した作業思想、参照優先順位、ユーザー個人の開発方針、停止条件、検証方針だけを置いた。
- [ ] 実プロジェクト固有の test / build / deploy / rollback コマンド、secret、環境名、remote URL を書いていない。
- [ ] `agentops` の `rules/`、`skills/`、`workflows/` は候補カタログとして扱い、機械的に全量反映する表現にしていない。
- [ ] `templates/claude/` または `templates/codex/` を素材として使う場合も、対象 CLI の現在仕様に合わせて生成し直した。
- [ ] CLI 固有の settings / config / hooks / permission / sandbox / approval の具体値を、本文へ固定しすぎていない。
- [ ] 長い手順、観点別チェック、反復的な作業は、必要に応じて skills、workflows、project docs、`.agentops` へ分ける方針にした。
- [ ] 反映後に、対象 CLI が実際にグローバル指示とプロジェクト指示を読んでいることを確認する手順を書いた。

## MCP

- [ ] MCP server の目的、scope、transport、認証方式、secret 管理、出力上限、ログの扱いを確認した。
- [ ] user scope と project scope の違いを確認し、共有すべきでない credential を project config に入れていない。
- [ ] MCP tool の permission / approval / allowlist / denylist を、対象 CLI の現在仕様に合わせて確認した。
- [ ] リモート MCP は OAuth、token 更新、失効、ネットワーク到達性、プロキシ、CA 証明書の扱いを確認した。
- [ ] 追加後に `mcp list` 相当、実 tool 呼び出し、失敗時ログ、削除手順を確認した。

## hooks

- [ ] hook は最後の軽いガードとして扱い、主要な検証は通常のテストや CI に残した。
- [ ] hook event、matcher、blocking 可否、timeout、標準入力/出力の仕様を公式 docs で確認した。
- [ ] hook のコマンドは冪等で、secret を出力せず、失敗時にユーザーが原因を読めるようにした。
- [ ] commit / push 前の protected branch と test gate は、対象プロジェクトの実コマンドに合わせた。
- [ ] hook を更新した後、成功ケースと失敗ケースをどちらも実行して確認した。

## skills / subagents

- [ ] global に置く skill / subagent と project に置く skill / subagent を分けた。
- [ ] `rules/catalog.md`、`skills/catalog.md`、`workflows/catalog.md` を使い、採用候補だけを選んだ。
- [ ] `templates/claude/`、`templates/codex/` の雛形を、公式 docs と実環境に合わせて調整した。
- [ ] skill は短い `description`、明確な発火条件、必要最小限の supporting files にした。
- [ ] 副作用がある skill は自動起動させず、手動起動や追加確認を前提にした。
- [ ] subagent は役割、入力、出力、tool 権限、MCP tool 継承、主 orchestrator の統合責任を明確にした。
- [ ] skill / subagent を追加した後、対象 CLI が現在セッションで読み込むか、再起動が必要かを確認した。

## permissions / sandbox / approval

- [ ] 既定は最小権限にし、危険な bypass / full access / yolo 相当をグローバル既定にしていない。
- [ ] shell、file read/write、network、MCP tool、browser、external command の許可境界を確認した。
- [ ] workspace-write の writable roots、`/tmp`、network access、追加 directory、project trust の扱いを確認した。
- [ ] approval policy は、通常作業、untrusted repository、CI、外部反映、destructive command で分けて考えた。
- [ ] 失敗時に sandbox 外で再実行する運用は、承認、ログ、対象コマンドの範囲を残す形にした。

## Codex app-server / CLI 更新後確認

- [ ] Codex CLI の version switch、再インストール、plugin / skill / config 変更後は、古い `codex app-server` が残っていないか確認した。
- [ ] `pgrep -a codex` などで app-server が複数残っていないことを確認し、必要なら Codex Desktop / CLI / app-server を終了して起動し直した。
- [ ] `~/.codex/tmp/arg0` と `PATH` の一時 wrapper が古いディレクトリを指していないことを確認した。
- [ ] `codex --version`、`codex --help`、sandbox 内の簡単な shell 実行、必要なら `codex sandbox` で通常実行が通ることを確認した。

## 反映後

- [ ] 実際に変更したファイル、変更しなかったファイル、未反映の残タスクを記録した。
- [ ] 対象 CLI で読み込み状態、MCP、hooks、skills、subagents、permission / sandbox / approval の実挙動を確認した。
- [ ] GitHub remote、branch、PR 運用、main 同期、hooks の導入状態を確認した。
- [ ] secret や token が diff、ログ、PR、handoff に出ていないことを確認した。
- [ ] 反映結果と検証結果をユーザーへ報告した。

## 確認先

- Claude Code: [memory](https://code.claude.com/docs/en/memory)、[settings](https://code.claude.com/docs/en/settings)、[MCP](https://code.claude.com/docs/en/mcp)、[hooks](https://code.claude.com/docs/en/hooks)、[skills](https://code.claude.com/docs/en/skills)、[subagents](https://code.claude.com/docs/en/sub-agents)
- Codex: [AGENTS.md](https://developers.openai.com/codex/guides/agents-md)、[config reference](https://developers.openai.com/codex/config-reference)、[hooks](https://developers.openai.com/codex/hooks)、[MCP](https://developers.openai.com/codex/mcp)、[skills](https://developers.openai.com/codex/skills)、[subagents](https://developers.openai.com/codex/subagents)、[agent approvals and security](https://developers.openai.com/codex/agent-approvals-security)
