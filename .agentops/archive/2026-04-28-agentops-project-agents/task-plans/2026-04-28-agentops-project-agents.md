# 2026-04-28 agentops project AGENTS

## 状態

- 完了。
- 作業ブランチ: `codex/agentops-project-agents`

## 前提条件

- 対象は `/home/otaku/agentops` リポジトリ内のプロジェクト指示と関連 docs。
- `~/.codex` の実設定ファイルは今回は直接変更しない。
- ルート `AGENTS.md` は、このリポジトリで作業する Codex へのプロジェクト固有指示として扱う。

## 不変条件

- 機密値、認証情報、環境変数ファイル、個人情報を `.agentops/` や docs に残さない。
- `config/codex/AGENTS.md` は `~/.codex/AGENTS.md` 用の雛形であり、実設定と混同しない。
- `main` へ直接 commit / push しない。

## 実行内容

1. ルート `AGENTS.md` を新規作成し、記録先の使い分けを明文化する。
2. `~/.codex` を触る作業では `~/.codex/.agentops/` にも記録を残すルールを明文化する。
3. README へルート `AGENTS.md` の参照導線を必要最小限で追加する。
4. 差分、docs 影響、自己レビューを確認する。

## 完了条件

- ルート `AGENTS.md` に project local と Codex global の記録先ルールが明記されている。
- README からプロジェクト固有指示を見つけられる。
- `git diff` で意図しない差分がない。
- 自己レビューで P0 / P1 / P2 の未対応指摘がない。

## 検証結果

- ルート `AGENTS.md` を作成した。
- README に `AGENTS.md` の参照導線を追加した。
- 自己レビューで P0 / P1 / P2 はなし。
- merge 前の最終レビューで P0 / P1 / P2 はなし。
- 今回は `~/.codex` の実ファイルを変更していない。

## 停止条件

- `~/.codex` 実ファイルへの書き込みが必要になった場合。
- 機密値や個人情報を扱う必要が出た場合。
- 記録先や運用方針についてユーザー判断が必要になった場合。
