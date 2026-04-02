---
name: task-manager
description: タスクのCRUD操作、検索、フィルタリングを行うスキル。タスクの追加・完了・更新・削除・取り下げ・検索の手順とデータ形式を定義する。
---

# タスク管理スキル

## データの場所

- 各PJのタスクデータ: `.ai-secretary/projects/<PJ名>/tasks.json`
- 定期タスク: `.ai-secretary/projects/<PJ名>/daily/tasks.json`, `weekly/tasks.json`, `monthly/tasks.json`

## タスクデータ構造

```json
{
  "id": "t-YYYYMMDD-NNN",
  "title": "タスク名",
  "status": "todo | in_progress | waiting | done",
  "deadline": {
    "date": "YYYY-MM-DD or null",
    "type": "hard | soft | asap | none",
    "note": "期限に関する補足"
  },
  "context": {
    "source": "meeting | chat | email | self",
    "source_detail": "発生元の詳細（会議名、日付等）",
    "requester": "依頼者名",
    "approver": "承認者名",
    "background": "タスクの背景・経緯",
    "behind_the_scenes": "VTTに残らない行間情報",
    "related_files": ["ファイルパスの配列"],
    "constraints": "制約条件"
  },
  "milestones": [
    { "title": "マイルストーン名", "date": "YYYY-MM-DD", "status": "todo | in_progress | done" }
  ],
  "review_history": [
    { "reviewer": "名前", "date": "YYYY-MM-DD", "feedback": "内容", "resolved": true }
  ],
  "starts_at": "YYYY-MM-DD or null — 着手可能日。この日付より前は一覧に表示しない",
  "tags": [],
  "created_at": "ISO8601",
  "updated_at": "ISO8601",
  "completed_at": "ISO8601 or null",
  "dropped": false,
  "drop_reason": null
}
```

## 操作手順

### 追加（add）
1. 該当PJの `knowledge.md` と `people.md` を読み込み、背景を把握する
2. 該当PJの tasks.json を読み込む
3. 新しいIDを採番（t-YYYYMMDD-NNN、同日の最大+1）
4. タイトルのみの場合、文脈からカテゴリ・期限を推定しユーザーに確認
5. 新しい関係者名が出てきた場合、**カタカナ表記でユーザーに確認**してから people.md への追記を提案する
6. 過去の同種タスク（patterns.json の `task_decomposition`）を参照し、サブタスク分解を提案する（該当パターンがあれば）
7. 同名・類似タイトルのタスクが過去に複数ある場合、`patterns.json` の `recurring_tasks` に記録を提案する
8. tasks.json に追加して保存
9. 保存後に読み直して構文確認
10. 必要に応じて `reminders.json` にリマインダーを登録する（単発会議の追加、フォロー期日など）

### 完了（done）
1. tasks.json から該当タスクを見つける
2. `date` コマンドで現在時刻を確認する
3. status を "done"、completed_at を現在時刻に更新
4. 保存後に読み直して構文確認
5. **学習記録（必須）:**
   a. 所要日数を計算（created_at → completed_at の差分）
   b. `.ai-secretary/global/patterns.json` の `time_estimation.accuracy_log` に以下を追加:
      ```json
      { "task_id": "...", "title": "...", "category": "...", "created_at": "YYYY-MM-DD", "completed_at": "YYYY-MM-DD", "days": N }
      ```
   c. マイルストーンがある場合、各段階の所要日数も `accuracy_log` に個別記録する
   d. 同種タスク（同じカテゴリ・類似タイトル）のパターンがあれば `task_decomposition` を更新する
   e. patterns.json 保存後に読み直して構文確認

### 取り下げ（drop）
1. tasks.json から該当タスクを見つける
2. dropped を true、drop_reason にユーザーの理由を記録
3. status は変更しない（取り下げ時点のステータスを保持）
4. 保存後に読み直して構文確認
5. **学習記録（必須）:**
   a. `.ai-secretary/global/patterns.json` の `dropped_task_patterns.observations` に特徴を追記する
      - 例: 「チャットで拾ったタスクで2週間以上催促がなかったもの」「依頼者不明で優先度が上がらなかったもの」
   b. patterns.json 保存後に読み直して構文確認

### 更新（update）
1. tasks.json から該当タスクを見つける
2. 指定されたフィールドを更新、updated_at を現在時刻に
3. 保存後に構文確認

### 一覧（list）
1. フィルタ指定がなければ全PJの tasks.json を走査
2. --cat でPJ絞り込み、--status でステータス絞り込み
3. dropped: true のタスクはデフォルトで非表示
4. starts_at が今日より未来のタスクは非表示（upcoming で確認）
5. 全PJの定期タスク（daily/, weekly/, monthly/ 配下の tasks.json）も走査し、通常タスクとは別セクション「定期タスク」として表示する

### 待機中一覧（upcoming）
1. 全PJの tasks.json を走査
2. starts_at が今日より未来のタスクのみ表示
3. starts_at が近い順にソートし、着手可能日を明示する

### 検索（search）
1. 全PJの tasks.json を走査
2. title, context.background, tags にキーワードが含まれるものを返す

## 定期タスクの完了記録

定期タスク（daily/, weekly/, monthly/ 配下の tasks.json）を完了にする場合、`completion_log` に記録を追加する。

### 手順
1. 該当する定期タスクの tasks.json を読み込む
2. completion_log に以下の形式で追加:
   - **日次**: `{ "period": "YYYY-MM-DD", "completed_at": "YYYY-MM-DD" }`
   - **週次**: `{ "period": "YYYY-Www", "completed_at": "YYYY-MM-DD" }`（ww はISO週番号）
   - **月次**: `{ "period": "YYYY-MM", "completed_at": "YYYY-MM-DD" }`
3. 保存後に読み直して構文確認

### 期間判定
- 新しい期間（翌日/翌週/翌月）になったら、その期間の記録がない＝未完了として扱う
- completion_log に該当期間のエントリがなければ未完了、あれば完了済み

### 日次タスクの completion_log 肥大化防止
- 日次タスクの completion_log は直近30日分のみ保持する
- 30日より古いエントリは記録時に自動で削除する

## ユーザーが提案を修正したとき

秘書の提案（優先度、カテゴリ推定、段取り等）をユーザーが修正した場合:
1. `.ai-secretary/global/patterns.json` の `priority_tendencies.observations` に修正内容を追記する
   - 例: `{ "date": "2026-04-02", "original": "...", "corrected": "...", "context": "..." }`
2. 傾向を言語化して記録する（次回の同種提案で反映するため）
3. patterns.json 保存後に構文確認

## 期限タイプ別の振る舞い

- **hard**: 3日前・前日・当日にアラート
- **soft**: 前日にリマインド。遅延時は再設定を提案
- **asap**: 毎日の一覧に表示し続ける
- **none**: 週次レビューで声かけ
