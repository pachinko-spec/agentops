# task: 01-discord-notify-cleanup

> parent_plan: `2026-05-02-discord-notify-cleanup-and-sentrux-catalog`
> status: approved

## 現在状態

approved。Phase 1 cross-review 通過後に着手する。

## 実行内容

### A. グローバル実反映 (PR 外、agentops repo 外の実ファイル)

1. `~/.claude/hooks/session_start.py`:
   - L86-87: `if root: notify_anttime_event("session-start", project=root)` を削除 (周辺の関連コメント含めて整える)
   - L48-54: `context` list の冒頭 5 行 (運用ルール再掲) を削除。L56 以降の git 配下情報は残す

2. `~/.codex/hooks/agentops_guard.py`:
   - L265: `notify_anttime_event("session-start", root or cwd)` を削除
   - L491: `notify_anttime_event("session-end", project)` を削除 (`stop()` 関数末尾の正常終了通知)
   - L241-247: `context` list の冒頭 4 行 (運用ルール再掲) を削除。L248 以降の git 配下情報は残す

3. `~/.claude/CLAUDE.md` § 通知方針:
   - retain 対象を「stop-failure / permission-wait / alert」の 3 種に揃える

4. `~/.claude/skills/notification-digest-writer/SKILL.md` (実体側):
   - ANT_TIME notify の retain 対象を update (lifecycle 通知が削除された旨)

5. `~/.claude/skills/project-localize-inventory/SKILL.md` (実体側):
   - sentrux を「導入候補ツール」として参照する文言追加 (詳細は task 02 で agentops repo 側 catalog を整備、本 skill では参照のみ)

### B. agentops repo 修正 (PR scope)

6. `docs/18-notification-strategy.md`: ANT_TIME 通知の retain 対象を 3 種 (stop-failure / permission-wait / alert) に明示。session-start / session-end の説明を「現状非発火、kind 自体は CLI に残存 (手動 alert / 拡張用)」と補記

(注: `config/claude/CLAUDE.md` 雛形は元々「通知方針」節を含まないため scope 外、実反映先 `~/.claude/CLAUDE.md` のみ更新。同様に agentops repo の `skills/` ディレクトリは `skills/README.md` で「実 SKILL.md 完成品は置かない、catalog のみ」と明示されているため、`skills/notification-digest-writer/SKILL.md` / `skills/project-localize-inventory/SKILL.md` の修正は repo 対象外。実体は A.4 / A.5 の `~/.claude/skills/` 側で実施)

## 検証

### 静的検証

- `python3 -m compileall ~/.claude/hooks/session_start.py ~/.codex/hooks/agentops_guard.py` exit 0
- 削除した行以外の挙動が変わっていないこと (Stop block / SECRET 検出 / 危険コマンド deny / `inspect_agentops` 出力) を diff 読み取りで確認

### Replayable 検証 (recommended、Codex P2 指摘反映)

- sample payload (例: `{"hook_event_name":"SessionStart","session_id":"test","cwd":"/home/otaku/agentops","source":"startup"}`) を hook script に stdin で流し、stdout JSON を取得
- 取得した JSON の `hookSpecificOutput.additionalContext` に運用ルール再掲 (`Put Claude Code global plan...` 等の定型 5 行) が **含まれない** ことを確認
- 同 JSON に動的情報 (`Git root: ...` / `Branch: ...` / `Dirty files: N` / `.agentops/...`) が **含まれる** ことを確認
- additionalContext は context window への system reminder injection であり通常 chat には表示されない (Claude docs 確認) ため、本検証は payload → JSON 経由で機械的に確認する

### 実機検証

- 新規 Claude Code セッションを起動し、ANT_TIME に session-start が来ないこと (実際の Discord 観察)
- 同様に Codex で session-start / session-end が来ないこと
- 品質ゲート違反シナリオで `stop-failure` が引き続き届くこと

## 停止条件

- 削除以外の意図しない変更が必要になった場合
- cross-review で P0/P1 残った場合
- secret 値の混入懸念

## 次セッションへ残すこと

- task 02 (sentrux カタログ追加) と並行・連続で進める
- Phase 4 (実装後 cross-review) → Phase 4.5 (archive) → Phase 5 (merge)
