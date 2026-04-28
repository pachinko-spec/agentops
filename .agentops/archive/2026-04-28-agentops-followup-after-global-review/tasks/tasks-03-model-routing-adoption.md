# Task 03: モデルルーティング雛形 / docs に採用例追記

- 親 plan: `2026-04-28-agentops-followup-after-global-review`
- 状態: 完了 (PR #26 で archive 移動済)

## 経緯

直前セッションで `~/.claude/agentops/model-catalog.yml` に `gpt-5.5` (`*_frontier` 系 Codex 候補) と `claude-sonnet-4-6` (軽量 3 ロール) を採用、`model_family` を `fast *` → `balanced *` へ同期。これを agentops 参照キット側に「採用例 (advisory)」として反映する。

agentops 雛形は `model_id: null` 方針 (固定 model id を埋めない) を維持する。

## 実行内容

### 1. `config/model-catalog.yml`

各ロール notes に採用例 (advisory) を追記。`model_id: null` は維持。

- `orchestrator_frontier` / `architect_frontier` / `review_frontier` の `target_cli: codex` 候補 notes 末尾:
  > 採用例 (advisory): 2026-04-28 時点でユーザーグローバル側に GPT 系の高推論モデル (例: `gpt-5.5` 系) を採用したケースあり。ChatGPT auth 限定の場合があり、API key auth 環境では下位モデルへ override されることに注意。実 model id は使用直前に公式 docs で確認する。
- `coding_fast` / `research_fast` / `docs_agent` の `target_cli: claude` 候補 notes 末尾:
  > 採用例 (advisory): 2026-04-28 時点で軽量タスクの baseline を Anthropic の中位モデル (例: `claude-sonnet-4-6` 系) に揃えたケースあり。サブスクプラン下で品質優先・cutoff 新しさ・1M context・近フロンティア性能を重視した判断。`model_family` も `fast *` から `balanced *` 系へ揃える運用が成立する。

`model_family` 値そのものは `fast *` のまま据え置き (advisory な雛形のため)。

### 2. `docs/04-model-routing.md`

「## 運用ルール」の前に新節「## 採用例 (参考)」を追加。

- 雛形側 `model_id: null` はそのまま。採用例は notes / 本節に集約
- cross-review 系 (`*_frontier` の codex 候補) で GPT 高推論モデル採用ケース紹介
- 軽量ロール 3 つ (coding_fast / research_fast / docs_agent) で Anthropic 中位モデル baseline 化ケース紹介
- 「実 model id は使用直前に公式 docs と CLI の現在仕様で確認」を末尾再強調
- 系列表記 (例: `gpt-5.5 系`、`claude-sonnet-4-6 系`) のみ。固定 model id は埋めない

### 3. `templates/claude/` 点検

ディレクトリ走査して固定モデル名 / haiku 参照例があれば軽微編集 (「使用直前に公式 docs で確認」へ寄せる)。新ファイルは作らない。

## 検証

- `grep -n "model_id: null" config/model-catalog.yml` の null コミットが維持されていること
- `grep -rn "haiku" /home/otaku/agentops --include='*.md' --include='*.yml'` が 0 件
- `grep -rn "gpt-5\.5\|claude-sonnet-4-6" /home/otaku/agentops` が「系列表記」「採用例」文脈以外で固定 id を埋めていないこと
- `docs/04-model-routing.md` の冒頭方針 (「固定モデル名を大量に埋め込まない」) と新節が矛盾しないこと

## 停止条件

- agentops 既存方針 (`model_id: null`) と採用例追記が両立しなくなる場合 → 統合判断をユーザーに相談

## 次セッションへ残すこと

なし
