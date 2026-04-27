# Gitとブランチ運用

## ルール

バージョン管理はGitHubを正とします。作業はブランチ、commit、push、GitHub上のPR、レビュー、GitHub上のmergeの流れで扱います。

## 禁止

- `main`、`master`、`develop` など保護対象ブランチへの直作業。
- mainへの直push。
- ローカルmergeだけで完了扱いすること。

## 完了確認

merge後は `main` に戻り、remoteの `main` を取得し、`git status --short --branch` で同期を確認します。
