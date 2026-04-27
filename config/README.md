# config

監視対象プロジェクト、陳腐化チェック対象、通知設定の雛形を置く場所です。

secretやDiscord webhook URLはこのリポジトリに保存しません。Context7 と Google Stitch の API key は shell profile（例: `.bashrv`）や OS secret に置き、`CONTEXT7_API_KEY` / `STITCH_API_KEY` として参照します。

## ファイル

- `claude/CLAUDE.md`: Claude Code のグローバル設定雛形
- `codex/AGENTS.md`: Codex のグローバル設定雛形
- `hooks.env.example`: hooks と CLI Wrapper 用の環境変数雛形
- `projects.yml`: `agentops-watch` の監視対象プロジェクト
- `freshness-sources.yml`: 陳腐化チェック対象の一次情報
- `model-catalog.yml`: 論理ロールと候補モデルの対応表
- `harness.yml`: project local harness spec の雛形

## 注意

- 正式な CLI/API model id は使用前に公式 docs で確認します。
- `AGENTOPS_DISCORD_WEBHOOK_URL` などの secret は shell profile、direnv、OS secret、CI secret に置きます。
