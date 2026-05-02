# task: 02-sentrux-catalog

> parent_plan: `2026-05-02-discord-notify-cleanup-and-sentrux-catalog`
> status: approved

## 現在状態

approved。Phase 1 cross-review 通過後に着手する。

## 実行内容 (本 task は agentops repo 内部のみ。`~/.claude/skills/<name>/SKILL.md` への参照追加は task 01 で扱う)

1. `docs/20-tooling-candidates.md` (新規、`applies-to: global`):
   - frontmatter: `name`, `description`, `applies-to: global`
   - 「導入候補ツール」設計思想 docs として独立化
   - sentrux: 概要、適合 project の特徴 (中規模以上で層境界を明示している repo / AI 生成コードの構造 gate が欲しい場合)、判定基準、`templates/projects/sentrux/.sentrux/rules.toml.template` 参照、CI / pre-commit 連携方針
   - 採用方針: 「強制導入は不可、project ごとに判断、雛形は agentops に置いてある」
   - 将来 tools 追加時の枠 (UA は将来検討対象として 1 行だけ言及、雛形は作らない)
2. `skills/catalog.md`: 「## tooling adoption candidates」section を新設、sentrux のみを 1 entry として記載 (docs/20 / templates/projects/sentrux/ 参照)
3. `templates/projects/sentrux/.sentrux/rules.toml.template` (新規):
   - 公式 README / sample (https://raw.githubusercontent.com/sentrux/sentrux/main/.sentrux/rules.toml) で確認できる現行スキーマで placeholder を作成
   - コメント済 (用語定義 / 各 field の意味 / 言語別の placeholder 例)
   - 現行 sentrux に合わせ、`[constraints]` / `[[layers]]` / `[[boundaries]]` の最小例を含める (`[rules]` ベースは旧仕様、採用しない)

(注: agentops repo の `skills/` ディレクトリは catalog のみで実 SKILL.md は置かない方針 (`skills/README.md` 明示)。`skills/project-localize-inventory/SKILL.md` の **実体**は `~/.claude/skills/project-localize-inventory/SKILL.md` にあり、そこへの sentrux 参照追加は task 01 (A.5) で実施する)

## 検証

- `docs/20-tooling-candidates.md` の frontmatter が `docs/00-glossary.md` の docs 区分早見表 (`global`) と整合
- `skills/catalog.md` の新 section が既存形式と整合
- `templates/projects/sentrux/.sentrux/rules.toml.template` が `sentrux` 公式 README 記載のスキーマと矛盾しない (公式 docs を WebFetch 確認)
- 各 file が secret / API key / personal data を含まない
- `skills/catalog.md` の新 entry と `docs/20-tooling-candidates.md` の相互リンクが繋がる
- `~/.claude/skills/project-localize-inventory/SKILL.md` 側の実反映 (sentrux 参照追加) は task 01 で実施され、本 task では参照のみ確認

## 停止条件

- sentrux 公式 README が確認できないか、rules.toml スキーマが大きく変わって雛形作成不能
- cross-review で P0/P1 残った場合

## 次セッターへ残すこと

- task 01 と一緒に 1 PR にまとめて push
- 別 plan として「sentrux を agentops repo 自体に試験導入」を将来検討
