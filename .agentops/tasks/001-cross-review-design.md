# 001 cross-review design policy

parent_plan: 2026-04-28-cross-review-design
status: in_progress

## 実行内容

- cross-review / cross-model review を、特定モデル固定ではなく、主エージェントとは別系列、別 CLI、別モデルファミリーの frontier reviewer を入れる設計思想として整理する。
- Codex 主体なら Claude Code / Anthropic 系、Claude Code 主体なら Codex / OpenAI 系が候補になりうることを docs と config template に反映する。
- 高リスク設計以外にも、新機能追加、リファクタリング、依存追加、API 契約変更、デプロイ影響、レビュー修正後に cross-review を検討する方針を catalog へ反映する。
- 採否、統合判断、停止判断は主 orchestrator が持つことを再確認する。

## 完了条件

- 対象 docs / catalog / config template の表現が、repo の「候補カタログ」方針と矛盾していない。
- 実 model id を固定していない。
- 検証と自己レビューが完了している。
- 未解決の P0/P1 がない。

## 検証

- `rg -n "cross-review|cross-model|クロスモデル|review_frontier|別系列|別 CLI|別モデル" README.md docs rules skills workflows templates config .agentops`
- `git diff --check`
- `scripts/agentops-watch check --projects config/projects.yml`
- 必要に応じて `python3 -m compileall tools`

## 完了時の後処理

- 完了した task は `.agentops/archive/2026-04-28-cross-review-design/tasks/` へ移す。
- 必要なら `.agentops/task-plans/current.md` と `.agentops/prompts/next-session.md` を更新する。

## 現在状態

- docs / catalog / config template の更新は完了。
- 検証と自己レビューは完了。
- 承認済み計画に基づき、重要確認が必要な場合を除いて commit / push / PR / merge / main 同期まで進める。

## 停止条件

- 実設定変更が必要になる。
- 未確認の model id を固定する必要が出る。
- レビュー修正またはテスト修正が2周を超える。
