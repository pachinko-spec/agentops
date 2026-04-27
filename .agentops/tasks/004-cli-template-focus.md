# 004 cli template focus

parent_plan: 2026-04-27-agentops-reference-kit-refactor
status: pending

## 実行内容

- Claude Code / Codex のグローバル設定を書くためのベストプラクティスとテンプレートに主軸を移す。
- `CLAUDE.md` / `AGENTS.md` の書き方、MCP、hooks、skills、subagents、permissions、sandbox、approval の確認観点を整理する。
- CLI ごとの差分は固定しすぎず、反映時点の公式 docs と実環境で確認する方針を維持する。

## 完了条件

- Claude Code 用テンプレートと Codex 用テンプレートの役割が明確になっている。
- 共通思想と CLI 固有設定の境界が明確になっている。
- グローバル設定反映時に使うチェックリスト案がある。

## 検証

- README の反映プロンプトと config 参照雛形が矛盾していない。
- CLI 固有仕様を固定しすぎていない。

## 完了時の後処理

- 完了した task は `.agentops/tasks/` 直下に残さず、対応する `.agentops/archive/<parent_plan>/tasks/` へ移す。
- 完了した `.agentops/task-plans/current.md` は `.agentops/archive/<parent_plan>/task-plans/` へ移し、次に着手する task に合わせて新しい `current.md` を作る。
- `.agentops/prompts/next-session.md` は、次に読むべき `current.md` と task を指す内容へ更新し、古い plan や完了済み task を入口にしない。
- `scripts/agentops-watch check --projects config/projects.yml` で、完了済み task が未完了件数に残っていないことを確認する。

## 停止条件

- 公式 docs 確認が必要な仕様を、未確認のまま固定しそうになった。
- Claude Code と Codex の差分を共通テンプレートで吸収できない。
