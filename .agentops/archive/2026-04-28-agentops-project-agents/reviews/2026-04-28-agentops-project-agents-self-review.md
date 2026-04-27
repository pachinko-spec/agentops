# 2026-04-28 agentops project AGENTS self-review

## 対象

- `AGENTS.md`
- `README.md`
- `.agentops/archive/2026-04-28-agentops-project-agents/task-plans/2026-04-28-agentops-project-agents.md`

## 観点

- `/home/otaku/agentops/.agentops/` と `~/.codex/.agentops/` の記録先が明確か。
- `config/codex/AGENTS.md` と `~/.codex/AGENTS.md` の区別が明確か。
- `~/.codex` の実設定変更前に計画と承認を要求しているか。
- 機密値や個人情報を記録しない方針が明確か。
- README からルート `AGENTS.md` へ到達できるか。

## 結果

- P0: なし。
- P1: なし。
- P2: なし。
- P3: なし。

## 検証

- ルート `AGENTS.md` に project local と Codex global の記録先を明記した。
- README の導入部とフォルダ構成へ `AGENTS.md` の参照を追加した。
- 今回は `~/.codex` の実ファイルを変更していない。
- merge 前の最終レビューで P0 / P1 / P2 の指摘はなし。

## 残リスク

- Codex 実グローバル設定への反映作業では、別途 `~/.codex/.agentops/` への記録と読み込み確認が必要。
