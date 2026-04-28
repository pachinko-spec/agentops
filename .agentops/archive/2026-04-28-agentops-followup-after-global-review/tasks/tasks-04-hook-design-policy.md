# Task 04: フック設計方針メモ追記

- 親 plan: `2026-04-28-agentops-followup-after-global-review`
- 状態: 進行中

## 経緯

直前セッションで `~/.claude/hooks/agentops_guard.py` (380 行集約) を `_common.py` + 6 event handler に分散、`SECRET_PATTERNS` を否定先読み付きへ修正、`PermissionRequest` を live 化、Python 維持理由を明文化した。

これを agentops 参照キット側に「判断方針」として記録する。**実フック雛形は新設しない** (agentops は実フックを持たない方針継続)。

## 実行内容

`/home/otaku/agentops/docs/09-hooks-quality-gates.md` の末尾に新節「## AI エージェント hook の設計方針メモ (参考)」を追加。

含める観点 (5 つ、抽象度は判断方針レベル):

1. **規模が増えたときの構成**: 単一ファイル集約から event 別ファイル分散 + 共通モジュール抽出への移行例。Claude Code event 一覧 (SessionStart / UserPromptSubmit / PreToolUse / PermissionRequest / PostToolUse / Stop 等) は最新仕様を公式 docs で確認
2. **言語選定**: 否定先読みが必要なら Python / Node。POSIX ERE は非対応。bottleneck は git subprocess で起動コスト差は無視可
3. **secret 検知の単語境界**: `(?<![A-Za-z0-9_-])sk-...` のように識別子 (例: `task-001-...`) 内の部分マッチを避ける否定先読みを使う。AWS / GitHub / Anthropic prefix も同様
4. **live と dead の区別**: `settings.json` に登録しないと live にならない。導入後に発火確認、auto モードでの動作も含む。dead handler を放置しない
5. **コメント / docstring 言語**: プロジェクト方針に従う

雛形コード / 個別パスは載せない。実装イメージはグローバル archive 側に残っているのでリンク不要 (`~/` 配下を docs から参照しない方針)。

## 検証

- `docs/09-hooks-quality-gates.md` の既存 git hooks 節が壊れていないこと
- 新節が「実フックを提供しない」方針を冒頭で明示していること
- `grep -rn "agentops_guard" /home/otaku/agentops` が新節含めて 0 件 (グローバル個別実装名を docs に埋めない)
- `grep -rn "claude-haiku\|gpt-5\.5" /home/otaku/agentops` が新節含めて該当ファイルに広がっていないこと

## 停止条件

- フック雛形 `templates/claude/hooks/` 新設が必要との結論になる → 別 plan へ切り出してユーザー承認
- 新節が雛形コード提供レベルまで膨らむ → スコープ縮小

## 次セッションへ残すこと

なし
