# hooks 品質ゲート

## 目的

hooks は、AI エージェントが危険な状態で commit / push しないための最後の軽いガードとして使う。

## 実装

| ファイル | 役割 |
| --- | --- |
| `scripts/check-protected-branch` | `main` / `master` / `develop` など保護対象ブランチでの作業を拒否する |
| `scripts/check-tests-before-push` | push 前に検証コマンドを実行する |
| `scripts/hooks/pre-commit` | branch gate を呼ぶ hook 雛形 |
| `scripts/hooks/pre-push` | branch gate と test gate を呼ぶ hook 雛形 |
| `scripts/install-hooks` | hook 雛形を `.git/hooks/` にインストールする |

## インストール

```sh
scripts/install-hooks --target . --mode copy
```

symlink で管理したい場合:

```sh
scripts/install-hooks --target . --mode symlink
```

## 環境変数

`config/hooks.env.example` を参照する。

| 変数 | 既定値 | 用途 |
| --- | --- | --- |
| `AGENTOPS_PROTECTED_BRANCHES` | `main master develop` | 保護対象ブランチ |
| `AGENTOPS_ALLOW_PROTECTED` | `0` | `1` の場合だけ保護対象ブランチでの作業を許可 |
| `AGENTOPS_TEST_COMMAND` | なし | pre-push で実行する検証コマンド |
| `AGENTOPS_ALLOW_NO_TESTS` | `0` | `1` の場合だけ検証コマンド未設定の push を許可 |

## DbC との関係

hooks は DbC の停止条件層のうち、commit / push 直前の品質ゲートを機械的に支える。DbC 5 条件（前提・不変・完了・禁止・停止）の単一真ソースは [DbCと品質ゲート](03-dbc-and-quality-gates.md) であり、本章ではそれを **hooks 文脈にどう適用するか** だけを記す。

hooks の適用範囲: 対象プロジェクトが Git リポジトリで `scripts/check-protected-branch` と `scripts/check-tests-before-push` を呼び出せる場合に有効化する。`pre-commit` で保護対象ブランチを拒否し、`pre-push` で検証コマンドを実行して失敗時に push を拒否する。検証コマンドが未定義で `AGENTOPS_ALLOW_NO_TESTS=1` も設定されていない場合や、破壊的操作・secret 参照が必要な場合は、hooks をスキップせずに作業を停止し DbC 停止条件として扱う。

## AI エージェント hook の設計方針メモ (参考)

agentops リポジトリ自体は AI エージェント実フックを持たない方針を継続する。本節はユーザーグローバル側 (`~/.claude/hooks/` など) で hook を運用するときの判断材料の参考メモであり、雛形コードは提供しない。設計時は対象 CLI の現在仕様を公式 docs で確認する。

### 規模が増えたときの構成

- 単一ファイル集約 (例: 数百行 1 ファイル) のまま event を増やすと、複数 event が同居して責務が曖昧になり、誤検知の局所修正や unit test も組みにくい。
- event 別ファイル分散 + 共通モジュール抽出 (例: `_common.py` + event handler 別ファイル) へ移行する構成例がある。Claude Code の event は `SessionStart` / `UserPromptSubmit` / `PreToolUse` / `PermissionRequest` / `PostToolUse` / `Stop` などが公式に定義されている。実装前に最新 event 一覧と payload 仕様を公式 docs で確認する。
- 分散構成は責務分離・unit test 容易性・誤検知ピンポイント修正で優位。集約のままでもよいが、handler 数が増えてきたら分散へ移す判断材料を持っておく。

### 言語選定

- secret 検知などの正規表現で否定先読み (`(?<!...)`) が必要なら、Python / Node など PCRE 互換系が向く。POSIX ERE (bash 標準) は否定先読み非対応のため、単純な単語境界しか書けない。
- 実 bottleneck は git subprocess 等の I/O が支配的で、ランタイム起動コスト差は通常無視できる。bash で書けるかどうかではなく、必要な正規表現が書けるかで言語を選ぶ。

### secret 検知の単語境界

- OpenAI 型 prefix のような `sk-...` 検知は、識別子 (例: `task-001-...`) 内の部分文字列を誤マッチしないよう、否定先読みで単語境界を入れる。例:
  - `(?<![A-Za-z0-9_-])sk-[A-Za-z0-9_-]{20,}`
- AWS / GitHub / Anthropic 等の prefix も、対象が token 全体になるよう同様の境界を確認する。実 token に近い長さ・charset を持つ偽陽性 (path、識別子、commit hash など) を grep で洗い出してから本番化する。

### live と dead の区別

- handler を実装しても、`settings.json` 等の hook 設定ブロックに event と matcher を登録しないと live にならない。導入後に各 event を実際に発火させて到達確認する (auto モード経由の挙動も含む)。
- dead handler を放置しない。意図して disable する場合は理由をコメントで残す。`PermissionRequest` のようにタイミングが限定される event は、特に live 確認を省略しない。

### コメント / docstring 言語

- プロジェクト全体の方針に従う。日本語ドキュメント主体のリポジトリでは、hook 内コメントも日本語に揃えると検索性・引き継ぎ容易性が上がる。混在は避ける。
