# DRY原則

## ルール

同じ判断基準、workflow、skill本文、設計思想を複数箇所に重複させません。

重複が必要な場合は、どこが正本で、どこが投影物かを明記します。

## 正本の基本配置

- 常時適用ルール: `rules/`
- 再利用可能な能力: `skills/`
- 作業手順: `workflows/`
- 背景、理由、設計思想: `docs/`
- 実設定へ反映する雛形: `config/`
- 実行補助と半自動化: `scripts/`

## adapterや設定雛形

`config/claude/CLAUDE.md` や `config/codex/AGENTS.md` は実設定への投影物です。正本を更新した場合は、必要な範囲だけ短く反映します。
