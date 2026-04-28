# Self review 001: agentops 参照キット反映

- 親 plan: `2026-04-28-agentops-followup-after-global-review`
- レビュー日: 2026-04-28 (Asia/Tokyo)
- レビュー範囲: 22 ファイル変更 + 6 新規 (.agentops/ 記録)
- 実施者: Claude Opus 4.7 (本セッションのメインエージェント)

## 経緯

`agentops-reviewer` 独立レビュー subagent を起動したが、Anthropic 側で Usage Policy 違反相当のエラーで失敗した (a8f3aba2d9fc1f730、188 秒、tool_use 45 で打ち切り)。エラー再現可能性が読めないため、本セッション内でセルフレビューを実施し、その結果を記録する。レビュー後段でユーザー判断により独立レビューが必要なら、PR 上で `gh` 経由または `/ultrareview` 等で外部依頼する。

## 観点別評価

### 1. 方針整合性 (advisory 性の維持)
- `config/model-catalog.yml`: 全 candidate で `model_id: null` を維持。採用例は notes 内 advisory として追記。✅
- `docs/04-model-routing.md`: 新節「## 採用例 (参考)」で「雛形側 `model_id: null` は維持する方針」「実 model id は使用直前に公式 docs と CLI の現在仕様で確認」を明示。冒頭方針 (「固定モデル名を大量に埋め込まない」) と矛盾なし。系列表記 (`gpt-5.5 系` / `claude-sonnet-4-6 系`) のみ。✅
- `templates/claude/hooks/` 新設なし、`docs/09` 新節で「agentops リポジトリ自体は AI エージェント実フックを持たない方針を継続」と冒頭明示。✅

### 2. AGENTS.md ↔ CLAUDE.md 対称性
- 5 行目相互参照: 完全対称 (`Claude Code` / `Codex` の差以外 wording 一致)。✅
- 章立て (位置づけ / 記録先 / `~/` 配下操作 / Git / 完了条件 / 停止条件): 既存対称性を維持。✅

### 3. config/claude ↔ config/codex 対称性
- `## cross-model 委譲`、`## セッションハンドオフ` 章タイトルが両ファイルで一致。✅
- 「主 orchestrator」結合修正も両ファイルで適用済み。✅

### 4. YAML 整合
- `python3 -c "import yaml; yaml.safe_load(...)"` 通過。✅
- `>-` (folded block scalar) は改行を空白に折りたたむため、parser 後の notes 値は連続文字列として読まれる。意味的に問題なし。✅

### 5. 用語統一
- 「主エージェント」「メインエージェント」: 実体ファイルに残存なし。`.agentops/tasks/tasks-02-...` 内のコード表記のみ (作業記録)。✅
- 「主 orchestrator + 助詞」結合 (例: `主 orchestratorと`): 全解消、半角空白挿入済み。✅
- 「クロスモデル」: 実体ファイルに残存なし。✅
- 「引き継ぎ」: 機能を指す術語は「ハンドオフ」へ統一。日常語 (引き継ぎ文書 / 引き継ぎ性 / 引き継ぎできる) は意図的に残した。判断は `tasks-02-terminology-consistency.md` に明記済み。✅

### 6. 採用例での model id 表記
- 全箇所で「系列表記」(例: `gpt-5.5 系`、`claude-sonnet-4-6 系`) を使用、生 id 埋め込みなし。✅

### 7. グローバル個別実装名の漏洩
- `agentops_guard.py` 等の名前が `docs/`、`config/`、`templates/`、`README.md`、`AGENTS.md`、`CLAUDE.md` のいずれにも埋まっていないことを確認 (`grep -rn agentops_guard` で実体ファイル 0 件)。✅

### 8. `~/` 配下への絶対参照
- 反映 docs (`docs/04`、`docs/09` 新節) は `~/.claude/...` への絶対パスを埋めていない。✅

### 9. 回帰確認
- AGENTS.md / CLAUDE.md 章立て、subagent / sub-agent / サブエージェント の表記 (今回スコープ外) には変更を加えていない。✅

## 指摘

- **P0 / P1**: 0 件
- **P2**: 0 件
- **P3 (改善余地、本作業範囲外、次回以降検討)**:
  - `docs/04-model-routing.md` 新節「採用例 (参考)」は「2026-04-28 時点」と日付固定で書いたため、半年〜1 年後に陳腐化する。年単位の review サイクルでメンテする必要があるが、雛形リポジトリでありステール容認の advisory なので緊急修正不要。次の cross-review 設計見直し時または `last_reviewed` 更新時に同期させる。
  - `config/model-catalog.yml` で `architect_frontier` の codex notes に「ChatGPT auth 限定の場合があるため、API key auth 環境ではダウングレードまたは別ロールへ振り直す。」と書いたが、`orchestrator_frontier` と `review_frontier` では「下位モデルへ override される」表記。意図として両方とも有効だが、表記を揃えるなら次回統一可能。今回は意味が一致しているので変更しない。

## マージ判断

未解決の P0 / P1 / P2 なし。P3 のみで、修正ループは継続しない。**PR 作成可** と判断。
