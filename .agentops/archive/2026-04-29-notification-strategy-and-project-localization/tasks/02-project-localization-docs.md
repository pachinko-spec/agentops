---
task-id: 02-project-localization-docs
parent-plan: ../plans/current.md
created: 2026-04-29
status: pending
pr-target: PR-C (プロジェクトローカライズ設計思想 docs)
branch: claude/project-localization-design-2026-04-29 (task 01 マージ後に作成)
---

# Task 02: プロジェクトローカライズ設計思想 docs (PR-C)

## 前提条件

- task 01 (PR-B) が main にマージ済 + main 同期済
- 既存 docs/14-real-project-template-policy.md はテンプレート配布視点のみ
- 既存 workflows/catalog.md の `project-intake` 行は 1 行のみ
- `~/dev/` 配下に 30 directory 存在し、本人が能動的に保守する主要 5 件 (ai-engine / ai-keiba / ai-utg / pachi-studio / ai-content-engine) を本 task の dry-run 対象とする
- 主要 5 件の 2026-04-29 観察:
  - CLAUDE.md+AGENTS.md 保持: 4 件 (ai-engine / ai-keiba / ai-utg / pachi-studio)
  - AGENTS.md+GEMINI.md+`.agent/` 保持 (CLAUDE.md なし): 1 件 (ai-content-engine)
  - `.codex` (0-byte file) 保持: 2 件 (ai-keiba / pachi-studio)
  - `.claude/` (dir) 保持: 4 件
  - `.ai/` (dir) 保持: 3 件 (ai-keiba / ai-utg / pachi-studio)

## 不変条件

- 本 task は **仕様 docs のみ**。`agentops localize` CLI 実装は別 plan
- 既存 docs/14 の役割を侵食しない (14=配布、19=既存への適用判定)
- `~/.claude/CLAUDE.md` 増分 +5 行以内
- 既存 5 プロジェクトの実マイグレーションに踏み込まない

## 完了条件

- `/home/otaku/agentops/docs/19-project-localization.md` 新規作成 (last_reviewed frontmatter)
  - 検出対象 inventory (痕跡ファイル一覧)
  - 競合判定マトリクス
  - 4 戦略の意思決定木 (greenfield / inventory-rebuild / coexistence / freeze)
  - 判定軸 (技術スタック × デプロイ先 × 痕跡鮮度 × 重要度 × 作業頻度)
  - 各戦略のチェックリスト
  - ~/dev/ 既存 5 プロジェクトへの dry-run 適用例 (1 戦略を一意に選べることの実証表)
- `/home/otaku/agentops/docs/14-real-project-template-policy.md` 編集 (docs/19 参照)
- `/home/otaku/agentops/docs/10-cli-wrapper.md` 編集 (`agentops localize` spec 行追加、実装は別 plan 注記)
- `/home/otaku/agentops/docs/17-cross-reference.md` 編集
- `/home/otaku/agentops/templates/claude/skill/agentops-localize/SKILL.md` 新規作成
- `/home/otaku/agentops/rules/catalog.md` 編集 (`project-integration-policy` 行追加)
- `/home/otaku/agentops/skills/catalog.md` 編集 (`project-localize-inventory` 行追加)
- `/home/otaku/agentops/workflows/catalog.md` 編集 (`project-localize` 行追加 + project-intake 前段への配置注記)
- `~/.claude/CLAUDE.md` 編集 (「既存プロジェクトのローカライズ」短い節 +5 行以内)
- markdown-link-check pass
- 4 戦略意思決定木で `~/dev/` 5 プロジェクトに対し dry-run で 1 戦略を一意に選べることを表で示す
- skill 雛形が Claude Code 公式 SKILL.md フォーマットに沿う
- Codex `review_frontier --effort high` cross-review P0/P1 0 件
- agentops archive ルールで commit 前に本 task + plan / task-plan を archive へ移動

## 禁止事項

- `agentops localize` CLI 実装に踏み込むこと
- 既存 5 プロジェクトの CLAUDE.md/AGENTS.md/.codex への実書き換え
- docs/14 の役割を変更すること

## 停止条件

- 4 戦略意思決定木で 1 プロジェクトに 2 戦略以上が該当 (判定軸が不十分)
- skill 雛形が Claude Code 公式仕様と齟齬がある
- レビュー修正 2 周超過
- `~/.claude/CLAUDE.md` 増分 +5 行超

## 検証手順

1. markdown-link-check (task 01 と同様)
2. `~/dev/` 主要 5 プロジェクトに対する dry-run 表が docs/19 に含まれること
3. **dry-run 表観察事実 verification**: docs/19 の表の各行を `ls -la ~/dev/<project>/` および `find ~/dev/<project> -maxdepth 2 -name "*.md" -o -type d -name ".*"` で観察し直し、痕跡 / 競合度の根拠が観察と一致すること
4. SKILL.md frontmatter の `allowed-tools` 仕様を Context7 / 公式 docs で確認し、Notes に反映
5. agentops-reviewer subagent で独立レビュー
6. Codex cross-review
7. P0/P1 反映後 reviewer 再走
8. `scripts/agentops archive task --task-id 02-project-localization-docs` 実行
9. commit → push → PR → auto-merge → main 同期
