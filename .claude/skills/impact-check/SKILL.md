---
name: impact-check
description: 構成変更の波及影響を分析するスキル。PJ追加/中断/削除・会議変更・関係者異動などのイベントに対し、影響ファイルと必要アクションをチェックリストで提示する。ヘルスチェックモードで全体整合性の診断も行う。
---

# 影響調査スキル（impact-check）

## 目的

`.ai-secretary/` 配下のデータは複数ファイルが相互に依存している。構成変更時に一部のファイルだけ更新して他を忘れると、ブリーフィングの会議漏れやタスクの表示不整合が発生する。このスキルは変更の波及範囲を可視化し、漏れを防ぐ。

## 依存関係マップ

### データ → データ（構成変更の波及）

```
config.json（PJ一覧）
  └→ projects/<PJ>/ ディレクトリの存在

meetings.json（定例会議定義）
  └→ weekly-schedule.json（今週の展開）
       └→ morning-briefing（スケジュール表示）

tasks.json（タスク）
  └→ reminders.json（関連タスクの参照）
  └→ morning-briefing（優先度提案）

people.md（関係者）
  ├→ global/people.md（マスタ）
  ├→ projects/<PJ>/people.md（PJ固有）
  └→ meetings.json の participants

daily/weekly/monthly tasks.json（定期タスク）
  └→ morning-briefing（完了判定）
```

### スキル → データ（スキル変更時の互換性）

```
スキル（.claude/skills/）
  ├→ 期待するフィールド → 既存データに存在するか？
  ├→ 期待する値の種類 → 既存データに未処理の値がないか？
  ├→ 期待するファイル → 全PJに存在するか？
  └→ 読み取りロジック → 既存データの解釈が変わらないか？
```

**スキルとデータの対応表**（※ 詳細は `.claude/docs/data-structure.md` の「関係するスキル・ルール」を参照）

| スキル | 読み取るデータ | 書き込むデータ |
|---|---|---|
| task-manager | tasks.json | tasks.json |
| meeting | meetings.json, weekly-schedule.json | meetings.json, weekly-schedule.json |
| morning-briefing | weekly-schedule.json, tasks.json, 定期tasks, reminders.json, patterns.json | reminders.json（処理済み更新） |
| setup | config.json | config.json, PJディレクトリ一式 |
| planning | tasks.json, patterns.json, knowledge.md | tasks.json（milestones） |
| prioritization | tasks.json, patterns.json, weekly-schedule.json | — |
| learning | tasks.json, patterns.json | patterns.json |
| knowledge-base | knowledge.md, people.md | knowledge.md, people.md |
| self-review | patterns.json（review_tendencies） | — |
| impact-check | 全ファイル（読み取り専用） | — |

## 2つのモード

### 1. イベント駆動モード

構成変更イベントを指定して実行する。

**使い方:** ユーザーが構成変更を伝えたとき、または他スキル（setup, meeting 等）の実行後に推奨される。

#### 対応イベントと影響マップ

---

#### EVENT: PJ追加

**トリガー:** 新しいPJが発足した

**チェックリスト:**
- [ ] `projects/<PJ>/` ディレクトリ一式が作成されているか（tasks.json, knowledge.md, people.md, meetings.json, meetings/_NAMING_RULE.md, files/, archive/, daily/, weekly/, monthly/）
- [ ] `global/config.json` の `projects` 配列にPJ名が追加されているか
- [ ] 定例会議がある場合、`meetings.json` に登録されているか
- [ ] `meetings.json` に登録した定例が `weekly-schedule.json` に展開されているか（今週分）
- [ ] 関係者が `global/people.md` に登録されているか（新規の人）
- [ ] 関係者が `projects/<PJ>/people.md` に登録されているか
- [ ] 定期タスクがあれば `daily/`, `weekly/`, `monthly/` の tasks.json に登録されているか

---

#### EVENT: PJ中断

**トリガー:** PJが一時停止になった

**チェックリスト:**
- [ ] `projects/<PJ>/tasks.json` の未完了タスクが `status: "suspended"` になっているか
- [ ] `projects/<PJ>/meetings.json` の定例に `"suspended": true` が付与されているか
- [ ] `weekly-schedule.json` から該当PJの定例会議が除外されているか（単発会議は残す）
- [ ] `reminders.json` に該当PJの related_task を持つリマインダーがあるか確認し、不要なら `done: true` にする提案
- [ ] PJ中断の経緯が `knowledge.md` に記録されているか（再開時の参考用）

---

#### EVENT: PJ再開

**トリガー:** 中断していたPJが再開した

**チェックリスト:**
- [ ] `projects/<PJ>/tasks.json` の suspended タスクを確認し、再開すべきものを `status: "todo"` に戻す提案
- [ ] `projects/<PJ>/meetings.json` の `"suspended": true` を `false` に変更（または削除）
- [ ] `weekly-schedule.json` に定例会議が再展開されているか
- [ ] `knowledge.md` に再開の経緯・新しいフェーズを記録する提案
- [ ] 中断中に変わった関係者・状況がないか確認を促す

---

#### EVENT: PJ削除

**トリガー:** PJが完全に終了・不要になった

**チェックリスト:**
- [ ] `global/config.json` の `projects` 配列からPJ名を削除
- [ ] `weekly-schedule.json` から該当PJの会議をすべて除外
- [ ] `reminders.json` で該当PJに関連するリマインダーを `done: true` に更新
- [ ] `global/people.md` で該当PJのみに関わる関係者がいれば、残すか確認
- [ ] `projects/<PJ>/` ディレクトリを `archive/` に移動する提案（即削除はしない）

---

#### EVENT: 定例会議の追加

**トリガー:** 新しい定例会議が設定された

**チェックリスト:**
- [ ] 該当PJの `meetings.json` に追加されているか
- [ ] `weekly-schedule.json` に今週分が展開されているか
- [ ] `day_of_week` が既存の会議と重複・隣接していないか（時間帯の確認）

---

#### EVENT: 定例会議の恒久変更

**トリガー:** 定例会議の曜日・時間・参加者が恒久的に変わった

**チェックリスト:**
- [ ] 該当PJの `meetings.json` が更新されているか
- [ ] `weekly-schedule.json` に変更が反映されているか（今週分の再展開）
- [ ] 変更後の時間帯が既存の会議と重複・隣接していないか

---

#### EVENT: 定例会議の削除

**トリガー:** 定例会議がなくなった

**チェックリスト:**
- [ ] 該当PJの `meetings.json` からエントリが削除されているか
- [ ] `weekly-schedule.json` から該当会議が除外されているか

---

#### EVENT: 関係者の異動/変更

**トリガー:** 関係者の役職・所属・担当が変わった、または退職・異動した

**チェックリスト:**
- [ ] `global/people.md` の該当者情報が更新されているか
- [ ] 該当者が関わる全PJの `projects/<PJ>/people.md` が更新されているか
- [ ] `meetings.json` の participants に該当者が含まれる会議があるか → 参加者の更新が必要か確認
- [ ] `tasks.json` の requester/approver に該当者がいるか → 後任への引き継ぎが必要か確認
- [ ] `reminders.json` に該当者に関連するリマインダーがあるか

---

#### EVENT: 定期タスクの追加/変更

**トリガー:** 日次・週次・月次の定期タスクが追加または変更された

**チェックリスト:**
- [ ] 該当の `daily/`, `weekly/`, `monthly/` の tasks.json が更新されているか
- [ ] `completion_log` の形式が正しいか（日次: YYYY-MM-DD, 週次: YYYY-Www, 月次: YYYY-MM）
- [ ] 週次・月次タスクに `deadline_rule` が設定されているか
- [ ] 週次タスクに `cycle_day` が設定されているか（ブリーフィングの完了判定に必要）
- [ ] 月次タスクに `cycle_date` が設定されているか（ブリーフィングの完了判定に必要）

---

#### EVENT: スキル変更

**トリガー:** `.claude/skills/*/SKILL.md` またはルール（`.claude/rules/*.md`）を変更した

**調査手順:**

1. **変更内容の分類**: 変更されたスキルが `.ai-secretary/` のどのデータを読み書きするか、上記「スキルとデータの対応表」で特定する

2. **以下の4観点でチェックする:**

| # | 観点 | チェック内容 | 例 |
|---|---|---|---|
| 1 | 新規フィールド | スキルが新たに期待するフィールドが、既存データに存在するか | meeting スキルが `suspended` フィールドを参照 → 既存 meetings.json にフィールドがない |
| 2 | 新規値 | スキルが新たに処理する値が、既存データに既に存在していないか（未処理状態で放置されていないか） | meeting スキルが `daily` を処理可能に → 既存 meetings.json に `day_of_week: "daily"` が既にある |
| 3 | 新規ファイル | スキルが新たに期待するファイルが、全PJに存在するか | スキルが `projects/<PJ>/quarterly/tasks.json` を参照 → 既存PJにそのディレクトリがない |
| 4 | 解釈変更 | スキルのロジック変更により、既存データの読み取り結果が変わらないか | weekly-schedule 生成時に `suspended` をスキップするロジック追加 → 既存データが正しく除外されるか |

3. **チェックリスト:**
- [ ] 観点1: 新規フィールドがある場合、既存データへのフィールド追加（またはデフォルト値の定義）が必要か
- [ ] 観点2: 新規値がある場合、既存データに未処理の値が放置されていないか
- [ ] 観点3: 新規ファイルがある場合、全PJにファイルが存在するか（なければ作成を提案）
- [ ] 観点4: 解釈変更がある場合、既存データで意図しない動作が起きないか（実データで検証）
- [ ] `data-structure.md` の更新が必要か（スキーマ変更、新フィールド、新ファイル等）
- [ ] 他スキルへの影響: 同じデータを読み書きする他スキルが、変更後のデータ形式に対応しているか

---

### 2. ヘルスチェックモード

イベント指定なしで全体の整合性を診断する。

**使い方:** 定期的に（週1回程度）、または「何かおかしい」と感じたときに実行。

**チェック項目:**

#### A. PJ構成の整合性
- `global/config.json` の `projects` 配列と `projects/` 配下の実ディレクトリが一致するか
- 各PJに必須ファイル（tasks.json, knowledge.md, people.md, meetings.json）が存在するか

#### B. 会議スケジュールの整合性
- `weekly-schedule.json` の `week` が今週の ISO 週番号と一致するか
- 各PJの `meetings.json`（`suspended` でないもの）が `weekly-schedule.json` に展開されているか
- `weekly-schedule.json` 内の `source_id` が実在する meetings.json エントリを指しているか

#### C. タスクとリマインダーの整合性
- `reminders.json` の `related_task` が実在するタスクを指しているか
- `done: false` のリマインダーで `trigger_date` が過去のものがないか（処理漏れ）

#### D. suspended 状態の整合性
- suspended な PJ のタスクがすべて `status: "suspended"` になっているか
- suspended な PJ の meetings.json がすべて `"suspended": true` になっているか
- suspended な定例が weekly-schedule.json に展開されていないか

#### E. 定期タスクの整合性
- `daily/`, `weekly/`, `monthly/` の tasks.json が valid な JSON か

#### F. スキルとデータの整合性
- `data-structure.md` に記載されたスキーマと、実際のデータファイルの構造が一致するか
- 各スキルが期待するフィールド（`suspended`, `day_of_week: "daily"` 等）が、対応するデータファイルで正しく処理されているか

### 出力形式

#### イベント駆動モード

```
## 影響調査: <イベント名>（<対象>）

### チェック結果

| # | 項目 | 状態 | 対応 |
|---|---|---|---|
| 1 | config.json にPJ追加 | ✅ 済 | — |
| 2 | meetings.json に定例登録 | ✅ 済 | — |
| 3 | weekly-schedule.json に展開 | ❌ 未 | 週次リセットの実行が必要 |
| ...

### 必要なアクション（未対応のみ）

1. weekly-schedule.json に今週分の定例を展開する
2. ...

実行しますか？
```

#### ヘルスチェックモード

```
## ヘルスチェック結果（YYYY-MM-DD）

### 全体サマリ
- ✅ 正常: N件
- ❌ 要対応: N件

### 要対応の詳細

| # | カテゴリ | 問題 | 推奨アクション |
|---|---|---|---|
| 1 | 会議 | weekly-schedule.json が先週のまま | 週次リセットを実行 |
| ...

対応しますか？
```

## 実行手順

### イベント駆動モード

1. イベントの種類と対象（PJ名、会議名、関係者名等）を特定する
2. 該当するイベントの影響マップを参照する
3. チェックリストの各項目について、**実際のファイルを読み取って**現在の状態を確認する
4. 結果を「チェック結果」表として提示する
5. 未対応の項目があれば「必要なアクション」として列挙し、ユーザーの承認を得てから実行する

### ヘルスチェックモード

1. `global/config.json` を読み込み、PJ一覧を取得する
2. チェック項目 A〜E を順に実行する
3. 各項目の結果を記録する
4. 結果を「ヘルスチェック結果」として提示する
5. 要対応の項目があれば推奨アクションを提示し、ユーザーの承認を得てから実行する

## 注意事項

- このスキルは**診断と提案**を行う。実際のファイル更新はユーザーの承認後に行う
- チェック結果で「✅ 済」の項目も表示する（安心感と網羅性の確認のため）
- 他スキル（setup, meeting 等）の実行後に推奨される場合がある
