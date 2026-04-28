# handoff: cross-reference skill / workflow 側逆参照列追加

> created_at: 2026-04-28
> source_plan: 2026-04-28-design-review-p0-p1
> source_task: 06-p1-03-cross-reference (PR #44 でマージ済)
> 想定対象 plan: 次 plan（未起票、本 plan 完了後に検討）
> 関連: docs/17-cross-reference.md, rules/catalog.md, skills/catalog.md, workflows/catalog.md

---

## 背景

task 06 (P1-03) で **rule 起点の最小マッピング表** (`docs/17-cross-reference.md`) と `rules/catalog.md` への 3 列追加（関連 skill / workflow / hook）を実装した。skill / workflow 側からの逆参照（skill → rule、workflow → rule の `関連 rule` 列追加）は task 06 不変条件 L33-35 と Codex 既存所見 P2-2 に基づき範囲外として、本 handoff へ申し送る。

## 想定スコープ

- `skills/catalog.md` の各 skill 行に `関連 rule（代表）` 列を追加
- `workflows/catalog.md` の各 workflow 行に `関連 rule（代表）` 列を追加
- skill / workflow から rule への戻りリンクを `docs/17-cross-reference.md` 経由で張る（または直接 rules/catalog.md へ）
- 1 skill / 1 workflow に複数 rule が紐づくケースの取り扱い方針を決める（代表 1 件 vs 全件列挙）

## なぜ task 06 範囲外にしたか

- 1 PR スコープを「rule 起点で 1 段階の最小マッピング」に絞らないと、rule 12 × skill 31 × workflow 15 の双方向化で半日工数を超える
- skill / workflow 側のマッピングを正確に行うには、各 skill / workflow の用途定義を再確認する必要があり、catalog 側の用語整理と connected で進めたい
- Codex Round 1 P2-2 (task 06 着手前) で同様のスコープ縮小が推奨されていた

## 次 plan で検討すべきこと

1. **代表 rule 1 件 vs 全件列挙**: docs/17 は rule 起点で代表 1 件のみだが、skill 側は 1 つの skill が複数 rule に対応するため代表 1 件では情報損失する可能性。例: `correctness-review` skill は review-policy だけでなく design-policy / secret-policy にも関連
2. **catalog.md vs docs/17 の責務分離**: docs/17 を「rule 起点表」に固定するか、「3 系統の双方向マトリクス表」に拡張するか
3. **frontmatter (last-reviewed) 同時追加**: 本 handoff に着手する時点で task 04 が完了し全 docs に YAML frontmatter が入っているため、新規 docs/* がある場合は同形式で揃える
4. **skill / workflow 側に hook 列も追加するか**: rule 経由で hook に辿れるが、skill / workflow → hook の直接列があった方が読みやすい場合あり

## 推奨優先度

- **本 plan (`2026-04-28-design-review-p0-p1`) 完了後の新 plan で扱う**
- 単独 task として **S–M（半日以内）** を想定。代表 1 件方式なら S（1h）、全件列挙方式なら M（半日）
- 本 plan の他 task（04 / 08 / 09）はいずれも本 handoff に依存しないため、優先度は中

## 関連 PR / commit / file

- PR #44 (task 06 本体): docs/17-cross-reference.md 新規 + rules/catalog.md 列追加
- archive: `.agentops/archive/2026-04-28-design-review-p0-p1/tasks/06-p1-03-cross-reference.md`
- review: `.agentops/reviews/p1-03.md`
- 本 plan §11 リスク欄「skills / workflows 側の逆参照列追加は task 06 範囲外で次 plan の handoff 候補」
