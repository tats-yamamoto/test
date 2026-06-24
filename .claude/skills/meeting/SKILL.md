---
name: meeting
description: 会議の一覧表示・追加・変更・キャンセル・週次リセットを行うスキル。定例会議と単発会議の両方を管理する。
---

# 会議管理スキル

## データの場所

- 定例会議の定義: `.ai-secretary/projects/<PJ>/meetings.json`
- 今週のスケジュール: `.ai-secretary/global/weekly-schedule.json`

## 前提ルール

- 操作前に `date` コマンドで現在時刻を確認する
- 会議操作時も該当PJの `knowledge.md`, `people.md` は必ず参照する
- 定例会議の「今週分だけの変更」は `weekly-schedule.json` のみ更新（`meetings.json` は変えない）
- 定例会議自体の恒久的な変更は `meetings.json` を更新
- JSON を書き込んだ後は必ず読み直して構文確認する
- 実行前にユーザーの承認を得る
- 会議には任意で `mode`（`相談` / `決定` / `報告`）を持たせられる。これは抽出時のデフォルトの構え（決定が出る前提か、発散主体か）を決めるヒント。未設定なら中立に扱う。※レビュー・面談は learning 等の専用フローで扱うため mode は付けない（→ `core-principles.md`「発散と収束の区別」）

## 機能

### 1. 一覧（list）

`weekly-schedule.json` から今週の会議一覧を表示する。

**手順:**
1. `.ai-secretary/global/weekly-schedule.json` を読み込む
2. `status` が `cancelled` でないものを抽出
3. 曜日ごとにグループ化して表示
4. 各会議について以下を表示:
   - 時間、タイトル、PJ名、参加者
   - status が `rescheduled` の場合は note も表示
   - prep（準備物）があれば表示

**表示例:**
```
## 今週の会議（2026-W14）

### 月曜（3/30）
会議なし

### 火曜（3/31）
- 13:00-13:30 週次報告会（直接業務）※通常月曜→今週は火曜にリスケ
- 15:00-16:00 全体定例（KaizenConnect）
- 17:00-18:00 車いすPJ定例（車いすPJ）

...
```

### 2. 追加（add）

#### 単発会議の追加
`weekly-schedule.json` に直接追加する。

**手順:**
1. ユーザーから以下をヒアリング: タイトル、日付、時間、参加者、PJ、目的、モード（相談/決定/報告、任意）
2. 新しいエントリを作成（id は `ws-XXX` で連番、source_id は null）
3. `weekly-schedule.json` に追加
4. 構文確認

**エントリ例:**
```json
{
  "id": "ws-007",
  "source_id": null,
  "title": "臨時打合せ",
  "date": "2026-03-31",
  "time": "10:00-10:30",
  "participants": ["カタオカ"],
  "purpose": "急ぎの相談",
  "mode": "相談",
  "project": "KaizenConnect",
  "status": "scheduled",
  "note": "単発"
}
```

#### 定例会議の追加
該当PJの `meetings.json` に追加する。

**手順:**
1. ユーザーから以下をヒアリング: タイトル、曜日、時間、参加者、PJ、目的、モード（相談/決定/報告、任意）
2. 該当PJの `meetings.json` に追加（id は `mtg-r-{PJ略称}-NNN` で連番。例: `mtg-r-cb-001`）
3. 構文確認
4. 今週分を `weekly-schedule.json` にも展開

### 3. 変更（update）

今週分のリスケ・時間変更等。

**手順:**
1. ユーザーから変更対象と変更内容をヒアリング
2. `weekly-schedule.json` の該当エントリを更新
   - `status` を `"rescheduled"` に変更
   - `note` に変更理由を記録
   - 日付・時間等を更新
3. 構文確認

**注意:** `meetings.json` は変更しない（今週限りの変更のため）。恒久的な変更の場合はユーザーに確認の上 `meetings.json` も更新し、**impact-check スキル（イベント: 定例会議の恒久変更）の実行を推奨する**。

### 4. キャンセル（cancel）

今週分のキャンセル。

**手順:**
1. ユーザーからキャンセル対象をヒアリング
2. `weekly-schedule.json` の該当エントリの `status` を `"cancelled"` に変更
3. `note` にキャンセル理由を記録
4. 構文確認

### 5. 週次リセット

月曜朝に呼ばれる想定。各PJの `meetings.json` から定例を展開し、`weekly-schedule.json` を新しい週のデータで上書きする。

**手順:**
1. 今週の週番号と月曜〜金曜の日付を算出
2. `.ai-secretary/projects/` 配下の全PJの `meetings.json` を読み込む
3. 各定例会議について、`day_of_week` に対応する今週の日付を割り当て
4. `weekly-schedule.json` を新しいデータで上書き:
   - `week`: 今週の週番号（例: `"2026-W14"`）
   - `generated_from_recurring`: true
   - `meetings`: 展開した全定例会議（各定例の `purpose`・`mode` 等の属性はそのまま引き継ぐ）
5. id は `ws-001` から連番で振り直す
6. 全エントリの `status` は `"scheduled"`、`note` は null
7. 構文確認

**曜日と day_of_week の対応:**
- mon → 月曜、tue → 火曜、wed → 水曜、thu → 木曜、fri → 金曜
- daily → 月曜〜金曜の全日に展開（各日に1エントリずつ作成）

**suspended な定例会議の扱い:**
- `meetings.json` のエントリに `"suspended": true` がある場合、週次リセット時にスキップする（`weekly-schedule.json` に展開しない）
- PJ再開時に `suspended` を `false` にすれば、次回の週次リセットから自動的に復帰する

**タスクの related_meetings からの展開:**
- 週次リセット時に、全PJの `tasks.json` の `related_meetings` も走査する
- 今週の日付に該当する会議があれば `weekly-schedule.json` に追加する（source_id は null、note にタスクIDを記載）
- これにより、タスクに紐づく単発会議（キックオフ、面談等）が自動的にスケジュールに反映される
