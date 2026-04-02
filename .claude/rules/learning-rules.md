# 学習記録ルール

## タスク完了時（必須）

タスクを完了（done）にしたら、必ず以下を実行してください:

1. 完了タスクの所要日数を計算（created_at → completed_at の差分）
2. `.ai-secretary/global/patterns.json` の `time_estimation.accuracy_log` に記録
3. 同種タスク（同じカテゴリ・類似タイトル）のパターンがあれば `task_decomposition` を更新
4. サブタスク（マイルストーン）がある場合、各段階の所要日数も記録

## タスク取り下げ時（必須）

タスクをdrop（やらないことにした）したら、必ず以下を実行してください:

1. tasks.json の `dropped` を true にし、`drop_reason` にユーザーが述べた理由を記録
2. `patterns.json` の `dropped_task_patterns.observations` に特徴を追記
   - 例: 「チャットで拾ったタスクで2週間以上催促がなかったもの」

## レビューFB記録時（必須）

/review でFBを記録したら、必ず以下を実行してください:

1. tasks.json の `review_history` にFB内容を追加
2. 該当PJの `people.md` のレビュアーの項目に傾向を追記
   - 例: 「2026-03-28: 結論ファーストを求める指摘 → 結論ファースト重視の傾向」
3. `global/people.md` の該当者にも全般的な傾向として反映

## ユーザーが提案を修正したとき

秘書の提案（優先度、カテゴリ推定、段取り等）をユーザーが修正した場合:

1. `patterns.json` の `priority_tendencies.observations` に修正内容を追記
2. 次回の同種の提案で修正内容を反映できるよう、傾向を言語化して記録

## 新規情報の検出時

VTT/テキスト抽出やタスク追加で新しい用語・関係者・制約を検出したら:

1. knowledge.md またはpeople.md への追加をユーザーに提案してください
2. ユーザーが承認したら追記してください
3. 勝手に追加しないでください

## 繰り返しタスクの検出

同名・類似タイトルのタスクが定期的に発生していることを検出したら:

1. `patterns.json` の `recurring_tasks` に記録
2. 次回の発生時期が近づいたら「そろそろこれやりませんか？」と提案
