---
description: メール・報告書・議事録のドラフトを作成する
argument-hint: "<task-id> [--type email|report|minutes] または email <説明>"
---

drafter エージェントにドラフト作成を依頼してください。

## 事前準備（必須）

1. タスクIDが指定された場合、そのタスクの背景情報を確認する
2. 該当PJの `knowledge.md` と `people.md` を読み込む（関係者の好み・立場・力関係を把握）
3. `.ai-secretary/templates/` にテンプレートがあれば確認し、適用する

## ドラフト生成

`--type` で種類を指定:
- `email` — メール下書き
- `report` — 報告書・提案書
- `minutes` — 議事録整理

## 生成後の手順（必須）

1. ドラフトを表示し「このまま使いますか？修正しますか？」と確認する
2. 会話の中で新しい情報（運用ルール、制約、経緯、力関係、人物情報等）が出てきたら、knowledge.md や people.md への追記を提案する
