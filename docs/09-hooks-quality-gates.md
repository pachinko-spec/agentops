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

## DbC

前提条件:

- 対象プロジェクトが Git リポジトリである。
- hook から `scripts/check-protected-branch` と `scripts/check-tests-before-push` を呼べる。

不変条件:

- 保護対象ブランチへの直接 commit / push を許可しない。
- 検証コマンドが失敗した状態で push しない。

完了条件:

- `pre-commit` が保護対象ブランチを拒否する。
- `pre-push` が検証コマンドを実行し、失敗時に push を拒否する。

停止条件:

- 検証コマンドが未定義で、`AGENTOPS_ALLOW_NO_TESTS=1` も設定されていない。
- 破壊的操作や secret 参照が必要になった。
