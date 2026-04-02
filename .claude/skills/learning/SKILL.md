---
name: learning
description: レビューFB記録、パターン分析、学習状況確認、繰り返しタスク検出を行うスキル。ユーザーの業務パターンを蓄積し、提案精度を向上させる。
---

# 学習・パターン記録スキル

## データの場所

- 学習パターン: `.ai-secretary/global/patterns.json`
- タスクデータ: `.ai-secretary/projects/<PJ>/tasks.json`
- 関係者データ: `.ai-secretary/projects/<PJ>/people.md` および `.ai-secretary/global/people.md`

## 1. タスク完了時の記録（task-managerから呼ばれる）

タスクを完了（done）にしたら必ず実行:

1. 所要日数を計算（created_at → completed_at の差分）
2. `patterns.json` の `time_estimation.accuracy_log` に記録:
   ```json
   { "task_id": "...", "title": "...", "category": "...", "created_at": "YYYY-MM-DD", "completed_at": "YYYY-MM-DD", "days": N }
   ```
3. マイルストーンがある場合、各段階の所要日数も `accuracy_log` に個別記録
4. 同種タスク（同じカテゴリ・類似タイトル）のパターンがあれば `task_decomposition` を更新
5. マイルストーンの実績を `planning_history.observations` にも記録
6. patterns.json 保存後に読み直して構文確認

## 2. タスク取り下げ時の記録（task-managerから呼ばれる）

タスクを drop したら必ず実行:

1. `patterns.json` の `dropped_task_patterns.observations` に特徴を追記
   - 例: 「チャットで拾ったタスクで2週間以上催促がなかったもの」
   - 例: 「依頼者不明で優先度が上がらなかったもの」
2. patterns.json 保存後に読み直して構文確認

## 3. レビューFB記録

レビューフィードバックを受けたら実行:

1. tasks.json の該当タスクの `review_history` にFB内容を追加:
   ```json
   { "reviewer": "レビュアー名", "date": "YYYY-MM-DD", "feedback": "FB内容", "resolved": false }
   ```
2. 該当PJの `people.md` にレビュアーの傾向を追記（日付必須）
   - 例: 「2026-03-28: 結論ファーストを求める指摘 → 結論ファースト重視の傾向」
3. `global/people.md` の該当者にも全般的な傾向として反映
4. `patterns.json` の `review_tendencies.by_reviewer` に定量データを更新:
   ```json
   { "<レビュアー名>": { "total_reviews": N, "common_points": ["構成", "数字の根拠"], "last_review": "YYYY-MM-DD" } }
   ```
5. 保存後に構文確認
6. 傾向の分析をユーザーに共有:
   - 過去のFBと比較して一貫した傾向があれば伝える
   - 例: 「この方は3回連続で構成の指摘をしています。次回は構成を先に見せると良いかもしれません」

## 4. ユーザーが提案を修正した場合

秘書の提案（優先度、カテゴリ推定、段取り等）をユーザーが修正した場合:

1. `patterns.json` の `priority_tendencies.observations` に修正内容を追記:
   ```json
   { "date": "YYYY-MM-DD", "original": "...", "corrected": "...", "context": "..." }
   ```
2. 傾向を言語化して記録（次回の同種提案で反映するため）
3. patterns.json 保存後に構文確認

## 5. 繰り返しタスクの検出

同名・類似タイトルのタスクが定期的に発生していることを検出したら:

1. `patterns.json` の `recurring_tasks` に記録
2. 次回の発生時期が近づいたら「そろそろこれやりませんか？」と提案

## 6. 学習状況の確認

ユーザーから学習状況を問われた場合:

- **概要表示**: タスク完了記録件数、FB記録件数、検出パターン数等
- **パターン詳細**: タスク分解パターン、見積もり精度、レビュアー傾向等
- **改善提案**: 「報告書作成は想定より1日多めにバッファを取りましょう」等
- 誤った学習を見つけた場合、ユーザーが手動で修正できるよう案内する
