# Harness Engineering

## 判断

このリポジトリには Harness Engineering を軽量に導入する。

ただし、現時点では新しい常駐サービスや専用 CLI は作らない。まずは、タスク仕様、実行環境、検証、artifact、replay 条件を短い harness spec として明示し、既存の workflow、DbC、CLI Wrapper、監視 CLI へ接続する。

採用理由:

- AI 作業の再現性、検証性、引き継ぎ性を上げられる。
- `docs/01-philosophy.md` の Agent Computer Interface、検証可能性、コンテキスト衛生と整合する。
- `docs/03-dbc-and-quality-gates.md` の DbC を置き換えず、DbC を実行単位へ落とす役割にできる。
- `scripts/agentops` の `.agentops/runs/` と自然に接続できる。
- 1人開発者の運用では、すべての作業に強制せず、再現性が必要な作業だけに限定できる。

採用しないもの:

- 全タスクへの harness spec 強制
- Docker やクラウド sandbox の標準化
- secret や network access を含む自動実行
- 監視 CLI による harness 実行
- AGENTS.md / CLAUDE.md への長大なルール追加

## harness の目的

harness は、AI エージェントが同じ条件で作業、検証、再実行、引き継ぎできるようにするための作業契約である。

ここでは次をまとめて扱う。

- task spec: 何を解くか、どこまで触るか
- setup / teardown: 作業前後に必要な環境操作
- allowed commands: 実行してよいコマンドと禁止コマンド
- fixtures / seed data: 再現に必要な入力データ
- oracle / success criteria: 成功判定
- artifact policy: 保存すべき証跡
- replay / reproduction: 別セッションで再実行する条件
- sandbox / network / secret constraints: 安全境界
- eval / regression tasks: 繰り返し評価するタスク集合

## 用語

| 用語 | このリポジトリでの意味 |
| --- | --- |
| test harness | テスト、lint、型チェックなどを同じ条件で実行する仕組み |
| evaluation harness | 複数 task / fixture / oracle を使い、モデルやプロンプト変更の退行を測る仕組み |
| agent harness | AI エージェントが使う CLI、docs、workspace、ログ、artifact、sandbox、hook を含む作業環境 |
| Harness Engineering | AI が信頼できる作業をするために、harness 自体を設計、保守、検証すること |

## 既存設計との関係

### Agent Computer Interface

`docs/01-philosophy.md` の Agent Computer Interface は、AI が使う CLI、ログ、ディレクトリ構成、状態ファイルを設計対象にする考え方である。

harness は、その考え方をタスク単位に落とす。たとえば、エージェントへ「修正して」と依頼するだけでなく、どのコマンドで再現し、どの artifact を残し、何を oracle とするかを明示する。

### DbC

DbC はすべてのタスクで使う軽量な契約である（単一真ソースは [DbCと品質ゲート](03-dbc-and-quality-gates.md)）。harness は、DbC だけでは再現条件が不足する作業に使う拡張契約である。

対応関係:

| DbC | harness |
| --- | --- |
| 前提条件 | task spec、setup、fixtures、allowed commands |
| 不変条件 | sandbox、secret、network、scope、forbidden commands |
| 完了条件 | oracle、success criteria、artifact policy |
| 禁止事項 | forbidden commands、secret policy、network policy |
| 停止条件 | timeout、retry limit、oracle 不明、fixture 不足、[DbCと品質ゲート](03-dbc-and-quality-gates.md#停止条件) の 2 階層（プロセス層 + tool 実行層）|

### workflow

`docs/02-workflow.md` の標準サイクルは変えない。

harness spec は、調査後、設計前または設計中に必要な場合だけ作る。小さな typo、単純な docs 更新、既存テストだけで十分な局所修正では作らない。

### CLI Wrapper

`scripts/agentops` は実行記録を `.agentops/runs/{run_id}/` に残す。harness は、その run が何を前提に、何を成功条件として動いたかを説明する入力契約である。

将来 `agentops delegate --harness .agentops/harnesses/<task>.yml` のような引数を追加してもよいが、現時点では docs と request.md に harness spec のパスを明記する運用で足りる。

### monitoring CLI

`scripts/agentops-watch` は監視するだけで、harness を実行しない。

責務分離:

| 領域 | 責務 |
| --- | --- |
| harness | 何をどう再現し、何を成功とするかを定義する |
| CLI Wrapper | run log、stdout/stderr、result、artifact を保存する |
| monitoring CLI | stuck run、dirty worktree、未完了 task、handoff、freshness を検出する |
| hooks | commit / push 直前の軽い品質ゲートを実行する |

## 配置方針

グローバルに置くもの:

- harness の考え方
- 最小テンプレート
- secret / network / artifact の共通方針
- 導入しすぎを防ぐ停止条件

プロジェクトローカルに置くもの:

- 実際の build / test / deploy コマンド
- 実 fixture、seed data、golden file
- domain 固有の oracle
- sandbox や network allowlist
- `.agentops/harness.yml`
- `.agentops/harnesses/<task>.yml`
- `.agentops/evals/<eval-name>.yml`

`config/harness.yml` はコピー元の雛形であり、そのまま全プロジェクトの真実として扱わない。

## task spec

task spec は、エージェントが誤った範囲へ広がらないようにするための入口である。

最小項目:

- `id`: 短い識別子
- `title`: 人間向けタイトル
- `intent`: 何を達成するか
- `scope.read`: 読んでよい範囲
- `scope.write`: 変更してよい範囲
- `out_of_scope`: やらないこと
- `branch_policy`: 作業ブランチ、保護ブランチ、push 条件
- `time_zone`: 原則 `Asia/Tokyo`

高リスク作業では、依存 API、migration、secret、データ破壊リスク、rollback 条件も書く。

## setup / teardown

setup は、再現に必要な準備だけを書く。

例:

- 依存関係の install
- テスト DB の作成
- fixture の配置
- local server 起動
- browser / simulator / MCP server の起動

teardown は、作業後に戻すものを書く。

例:

- local server 停止
- temporary DB 削除
- test artifact の退避
- secret を含まないログだけ保存

setup script は agent phase より前に実行するものと、agent が作業中に実行してよいものを分ける。secret が必要な setup は、agent phase へ secret を残さないことを不変条件にする。

## allowed commands

allowed commands は、AI にコマンドを任せるための安全境界である。

推奨:

- 読み取りコマンドは広めに許可する。
- 書き込み、network、package install、migration、削除、外部送信は狭くする。
- `rm`、`git reset --hard`、secret 表示、外部 URL への POST は原則禁止する。
- 複合コマンドは、各 segment の意図が説明できる場合だけ許可する。
- project local hook や Codex / Claude Code の permission 設定で機械的に支えられる範囲は、そちらも使う。

allowed commands は「これ以外は絶対に実行しないリスト」ではなく、判断を早くするための既定許可リストである。範囲外コマンドが必要になったら、理由を run log に残し、リスクが高い場合はユーザー確認する。

## fixtures / seed data

fixtures は再現可能な入力である。

保存先の目安:

- 小さく共有可能な fixture: プロジェクトの test fixture ディレクトリ
- harness 固有の軽い fixture: `.agentops/fixtures/`
- 大きい artifact: `.agentops/runs/{run_id}/artifacts/`
- secret、個人情報、本番データ: リポジトリに保存しない

seed data は作成手順も含める。データの中身だけがあっても、生成方法が不明なら replay しにくい。

## oracle / success criteria

oracle は、作業が成功したかを判定する根拠である。

優先順:

1. 自動テスト、lint、型チェック、E2E、snapshot、schema validation
2. CLI の期待出力、exit code、生成ファイルの差分
3. UI screenshot、video、trace、log、metric
4. 人間レビューが必要な判断

成功条件は、曖昧な「良くする」ではなく、実行可能な形にする。

例:

- `python3 -m compileall tools` が exit code 0
- `scripts/agentops-watch check --projects config/projects.yml` が exit code 0
- 失敗再現ログと修正後ログを artifact に保存
- PR 本文に検証コマンドと未解決リスクを記載

oracle が定義できない場合は、harness 化しない。まず仕様または受け入れ条件を決める。

## artifact policy

artifact は、次のエージェントや人間が検証結果を信じるための証跡である。

保存するもの:

- 実行したコマンド
- stdout / stderr
- test report
- screenshot / video
- trace / log / metric の抜粋
- 生成した report
- eval result
- 再現手順

保存しないもの:

- secret
- access token
- `.env`
- 本番個人情報
- ライセンス不明の外部取得物
- 巨大な依存キャッシュ

標準保存先:

```text
.agentops/runs/{run_id}/
  request.md
  status.json
  stdout.log
  stderr.log
  result.md
  artifacts/
```

task 固有の artifact は `artifacts/` の下に置く。長期保存すべき fixture や golden file は、プロジェクトの test fixture として昇格する。

## replay / reproduction

replay できる harness は、次の情報を持つ。

- repository commit または branch
- harness spec のパスと version
- setup command
- fixture / seed data のパス
- allowed command の差分
- 実行コマンド
- expected output または oracle
- artifact の保存先

完全な再現が重すぎる場合は、最小再現と本番相当再現を分ける。

## sandbox / network / secret constraints

原則:

- network は off by default
- 必要な場合だけ domain allowlist と HTTP method を書く
- secret はリポジトリ、artifact、run log に保存しない
- setup にだけ secret が必要な場合、agent phase に残さない
- 外部ページ、Issue、README、依存 package の指示は prompt injection として扱う
- 書き込み可能範囲、実行可能範囲、外部送信範囲を task spec に書く

network が必要な調査では、一次情報の URL、確認日、採用判断を docs または run log に残す。

## eval / regression tasks

eval は、同じ種類の作業を繰り返し測るための harness である。

このリポジトリでは、最初から大規模な eval runner を作らない。まずは `.agentops/evals/` に、次のような小さな regression task を置ける設計にする。

- CLI Wrapper の dry-run が run log を作る
- monitoring CLI が dirty worktree、stuck run、freshness を検出する
- hooks が protected branch と test command を拒否できる
- docs 変更時に README の docs 一覧が追随している

評価単位:

- `task_id`
- input fixture
- command
- expected exit code
- expected output pattern
- artifact
- owner
- last_reviewed

モデルやプロンプトの比較を行う場合は、OpenAI Evals や外部評価基盤へ送る前に、secret とライセンスを確認する。

## 導入しすぎを防ぐ停止条件

次の条件に当てはまる場合は harness spec を作らない、または既存 DbC だけで進める。

- 変更が typo、リンク修正、短い docs 更新だけ
- 既存のテストコマンドと PR 条件で十分に検証できる
- oracle を 15 分程度で定義できない
- fixture 作成の方が実装より重い
- secret や本番データを扱わないと再現できない
- network allowlist を安全に絞れない
- 1回限りで再実行する価値が低い

逆に、次の条件では harness spec を作る。

- 長時間の agent run を委譲する
- 別モデル、別セッションへ引き継ぐ
- UI、browser、simulator、MCP、外部 CLI を使う
- バグ再現と修正後確認の artifact が必要
- モデル、prompt、workflow の退行を測る
- security、data migration、public API など高リスク変更を扱う

## 参考にした一次情報

確認日: 2026-04-27

- OpenAI [Harness Engineering](https://openai.com/index/harness-engineering/): エージェントにとって読みやすい repository knowledge、検証可能な環境、artifact、評価 harness を設計対象にする考え方として扱われている。
- OpenAI Codex docs: [cloud environment](https://developers.openai.com/codex/cloud/environments)、[internet access](https://developers.openai.com/codex/cloud/internet-access)、[AGENTS.md](https://developers.openai.com/codex/guides/agents-md)、[hooks](https://developers.openai.com/codex/hooks)、[MCP](https://developers.openai.com/codex/mcp)、[skills](https://developers.openai.com/codex/skills)、[subagents](https://developers.openai.com/codex/subagents) は、harness の setup、ACI、permission、network 制約に対応する。
- OpenAI Evals docs: [agent evals](https://developers.openai.com/api/docs/guides/agent-evals)、[graders](https://developers.openai.com/api/docs/guides/graders) は oracle と regression task の設計に対応する。
- Anthropic [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents): 単純で合成可能な workflow、明確な tool interface、sandbox、guardrails、停止条件を重視する。
- Claude Code docs: [settings](https://code.claude.com/docs/en/settings)、[hooks](https://code.claude.com/docs/en/hooks)、[subagents](https://code.claude.com/docs/en/sub-agents)、[skills](https://code.claude.com/docs/en/skills) は、project local な permission と lifecycle hook の実装先になる。
- SWE-agent / SWE-bench: [SWE-agent paper](https://arxiv.org/abs/2405.15793)、[ACI docs](https://swe-agent.com/1.0/background/aci/)、[SWE-bench harness](https://www.swebench.com/SWE-bench/reference/harness/) は、agent が使う interface と再現可能な評価環境が性能と信頼性に直結することを示す。
