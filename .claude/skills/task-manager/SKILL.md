---
name: task-manager
description: タスクのCRUD操作、検索、フィルタリングを行うスキル。タスクの追加・完了・更新・削除・取り下げ・検索の手順とデータ形式を定義する。
---

# タスク管理スキル

## データの場所

- 各PJのタスクデータ: `.ai-secretary/projects/<PJ名>/tasks.json`（アクティブなタスクのみ）
- アーカイブ: `.ai-secretary/projects/<PJ名>/tasks_archive.json`（done/dropped のタスク）
- 定期タスク: `.ai-secretary/projects/<PJ名>/daily/tasks.json`, `weekly/tasks.json`, `monthly/tasks.json`

### アーカイブの仕組み

- `tasks.json` には **todo / in_progress / waiting / suspended** のタスクのみ保持する
- タスクが **done** または **dropped** になったら `tasks_archive.json` に移動し、`tasks.json` から削除する
- `tasks_archive.json` がまだ存在しない場合は空配列 `[]` で新規作成してからタスクを追加する
- 一覧表示（list）ではアーカイブを読まない。過去タスクの検索時のみアーカイブを参照する

## タスクデータ構造

```json
{
  "id": "t-YYYYMMDD-NNN",
  "title": "タスク名",
  "status": "todo | in_progress | waiting | done",
  "assignee": "担当者名 or null",
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
  "todos": [
    { "title": "アクション名", "status": "todo | done" }
  ],
  "milestones": [
    { "title": "チェックポイント名", "date": "YYYY-MM-DD", "done": false }
  ],
  "related_meetings": [
    { "title": "会議名", "date": "YYYY-MM-DD", "time": "HH:MM-HH:MM or null", "participants": ["名前"] }
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

## タスク登録の粒度基準

- 「完了」の定義が明確なもの（成果物・アクションがある）だけをタスクとして登録する
- 「〜に出る」「〜を続ける」のような継続的な日常動作はタスク化しない
  - 例: NG「定例会議に参加開始」→ OK「会議でのキャッチアップ内容を整理する」

## タスクの表示タイミング原則

**タスクは「今やることがある」ときだけ表示する。**

- タスクの最初のアクションが会議（キックオフ、打合せ等）の後に発生する場合、`starts_at` をその会議の日付に設定する
- 会議自体は `related_meetings` に記録し、`weekly-schedule.json` 側で管理する（タスク一覧ではなくスケジュールに表示）
- 会議後にTODO・マイルストーンが具体化したら、タスクに追加する
- `starts_at` 到達前は「待機中」として通常一覧から非表示（upcoming で確認可能）

例: 部署紹介（キックオフ4/8、本番5/20）
- キックオフ前: タスク非表示（`starts_at: "2026-04-08"`）。キックオフは会議スケジュールに表示
- キックオフ後: todos・milestonesを追加、タスクがアクティブに表示される

## 操作手順

### 追加（add）
1. 該当PJの `knowledge.md` と `people.md` を読み込み、背景を把握する
2. 該当PJの tasks.json を読み込む
3. 新しいIDを採番（t-YYYYMMDD-NNN、同日の最大+1）
4. タイトルのみの場合、文脈からカテゴリ・期限を推定しユーザーに確認
5. **starts_at の判断**: タスクの最初のアクションが会議の後に発生する場合、`starts_at` をその会議日に設定し、会議を `related_meetings` に登録する。今すぐやることがあるなら `starts_at` は null
6. **assignee の判断**: 自分がやるタスクなら `null` または `"ヤマモト"`。他人のアクションをPM視点でウォッチしたい場合は担当者名を指定（人名・「2年目」等の役割表記も可）
7. 新しい関係者名が出てきた場合、**カタカナ表記でユーザーに確認**してから people.md への追記を提案する
8. tasks.json に追加して保存
9. 保存後に読み直して構文確認
10. 必要に応じて `reminders.json` にリマインダーを登録する
11. `related_meetings` に登録した会議が今週に含まれる場合、`weekly-schedule.json` にも追加する

※ マイルストーン分解が必要な場合は planning スキルを使用
※ 優先度の位置づけ提案は prioritization スキルを使用

### TODO完了時の starts_at 自動提案

タスクのTODOを完了にした結果、**全TODOが done かつ未来の related_meetings が残っている**場合:

1. 「全てのTODOが完了しました。次は〇〇（会議名, MM/DD）の後にアクションが発生する可能性があります」と報告
2. `starts_at` を次の related_meetings の日付に設定することを提案
3. ユーザーが承認したら `starts_at` を更新し、タスクは会議日まで非表示になる

※ この判定はhook（todo-completion-check.py）でも自動検出される

### 完了（done）
1. tasks.json から該当タスクを見つける
2. `date` コマンドで現在時刻を確認する
3. status を "done"、completed_at を現在時刻に更新
4. 保存後に読み直して構文確認
5. **該当タスクを tasks_archive.json に移動し、tasks.json から削除する**
6. **learning スキルのタスク完了時記録を実行する**

### 取り下げ（drop）
1. tasks.json から該当タスクを見つける
2. dropped を true、drop_reason にユーザーの理由を記録
3. status は変更しない（取り下げ時点のステータスを保持）
4. 保存後に読み直して構文確認
5. **該当タスクを tasks_archive.json に移動し、tasks.json から削除する**
6. **learning スキルのタスク取り下げ時記録を実行する**

### 更新（update）
1. tasks.json から該当タスクを見つける
2. 指定されたフィールドを更新、updated_at を現在時刻に
3. 保存後に構文確認

### 一覧（list）
1. フィルタ指定がなければ全PJの tasks.json を走査
2. --cat でPJ絞り込み、--status でステータス絞り込み
3. dropped: true のタスクはデフォルトで非表示
4. starts_at が今日より未来のタスクは非表示（upcoming で確認）
5. suspended ステータスのタスクは非表示（PJ再開時に再表示）
6. **assignee が自分以外（null/"ヤマモト" 以外）のタスクは「ウォッチ中」枠で別表示**（PM視点で他人のアクションを追うタスク。日次TODOとは分ける）
7. 全PJの定期タスク（daily/, weekly/, monthly/ 配下の tasks.json）も走査し、通常タスクとは別セクション「定期タスク」として表示する
8. todos があるタスクは、進捗 `[完了数/全数]` を表示し、未完了のTODOを次の行に `└ TODO:` で表示する
9. milestones があるタスクは、直近の未完了マイルストーンを `└ MS:` で表示する
10. related_meetings があるタスクは、直近の未来の会議を `└ 会議:` で表示する
11. ウォッチ枠のタスクは担当者名を `[担当:シンカイ]` のように明示する

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

## 期限タイプ別の振る舞い

- **hard**: 3日前・前日・当日にアラート
- **soft**: 前日にリマインド。遅延時は再設定を提案
- **asap**: 毎日の一覧に表示し続ける
- **none**: 週次レビューで声かけ
