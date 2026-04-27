# 機能開発workflow

## 使う場面

実プロジェクトで新機能、バグ修正、UI改善、API変更、運用改善を設計からリリース準備まで進める時に使います。

## 手順

1. `project-intake.md` で対象プロジェクト、スタック、デプロイ先、検証コマンドを確認する。
2. 目的、非目的、利用者、完了条件、リスクを整理する。
3. 必要な design skill と implementation skill を選ぶ。
4. 影響範囲を frontend、backend、DB、API契約、認証、課金、docs、運用に分ける。
5. 実装前に計画を提示し、承認を得る。
6. 小さく実装し、lint、型チェック、テスト、必要ならE2Eとブラウザ確認を行う。
7. README、docs、API docs、runbook、release notes、環境変数説明の更新漏れを確認する。
8. `code-review.md` と必要な `skills/review/*` で自己レビューする。
9. リリース対象なら `release-readiness.md` で release / rollback / monitoring を確認する。

## 完了条件

- 実装、検証、docs更新、自己レビューが完了している。
- 未解決リスク、未実行テスト、延期したP2が明示されている。
- デプロイ先に影響がある場合、公式docs確認とrollback方針が残っている。
