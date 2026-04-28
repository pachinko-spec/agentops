# Task 01: AGENTS.md → CLAUDE.md 対称クロスリファレンス追加

- 親 plan: `2026-04-28-agentops-followup-after-global-review`
- 状態: 進行中

## 経緯

PR #24 (CLAUDE.md 新設) のレビューで「AGENTS.md 側にも CLAUDE.md への対称クロスリファレンスを入れるべき」と P2 指摘が残った。CLAUDE.md 5 行目には `Codex 向けの対応指示は同階層の AGENTS.md にあります` と相互参照記述があるが、AGENTS.md 側に対応する逆リンクがない非対称状態。

## 実行内容

`/home/otaku/agentops/AGENTS.md` の 3 行目 (リード文) の直後に、CLAUDE.md 5 行目と対称な 1 行を挿入する:

```
Claude Code 向けの対応指示は同階層の `CLAUDE.md` にあります。両ファイルは章立てを揃えてあるので、片方を更新したら他方も同期してください。
```

CLAUDE.md 側の文言と語尾レベルで完全対称になっているか目視確認する。

## 検証

- `git diff AGENTS.md` で 1 行追加のみであること
- `grep -n "対応指示は" AGENTS.md CLAUDE.md` で 2 ファイルが互いを参照していること
- AGENTS.md と CLAUDE.md を並べて、リード文 + 相互参照行 + 章立てが対称になっていることを目視

## 停止条件

- 章立てが想定外に乖離していた場合 → 同期作業のスコープ確認

## 次セッションへ残すこと

なし (本セッション内で完結予定)
