# archive

完了、中止、置き換え済みのplan単位の記録をまとめる場所です。

## 構成

```text
.agentops/archive/<plan-id>/
  plan.md
  task-plans/
  tasks/
  reviews/
  runs/
```

`tasks/` 直下の未完了タスク数と監視CLIの表示を一致させるため、完了済みtaskは必ず対応するarchiveへ移します。
