# データ取扱いルール

※ `.ai-secretary/` の全体構成・各ファイルの構造は `.claude/docs/data-structure.md` を参照

## ファイルパス

- すべてのデータはプロジェクトルートの `.ai-secretary/` 配下に格納されています
- PJ単位のデータ: `.ai-secretary/projects/<PJ名>/`
- グローバルデータ: `.ai-secretary/global/`

## ファイル形式の使い分け

- **JSON**: tasks.json, patterns.json, config.json — 検索・フィルタ・数値集計が必要な構造データ
- **Markdown**: knowledge.md, people.md, user-profile.md — 文章主体のデータ

## JSON操作のルール

- tasks.json を書き込んだ後、必ず読み直して構文が正しいことを確認してください
- patterns.json を書き込んだ後も同様に構文確認してください
- JSONのIDは `t-YYYYMMDD-NNN` 形式で採番してください（例: t-20260326-001）
- 既存のデータを上書きする場合、変更前の内容を確認してから書き込んでください

## Markdown操作のルール

- knowledge.md, people.md 等に追記する際、既存の内容を壊さないでください
- 新しいセクションを追加する場合、既存の構造（見出しレベル等）に合わせてください
- 日付付きの情報（決定事項、レビュー傾向等）は日付を必ず記録してください

## 関係者名の表記

- VTT等の音声認識から拾った名前は**カタカナ表記**に統一してください
- 音声認識は漢字変換を間違えることが多いため、漢字で登録しないでください
- 名前を登録する前に、必ずユーザーにカタカナ表記で確認を取ってください

## タスク一覧の表示ルール

- `suspended` ステータスのタスクは非表示（PJ再開時に再表示）
- `starts_at` が未来のタスクは「待機中」として別枠で表示
- todos があるタスクは、進捗 `[完了数/全数]` を表示し、未完了のTODOを `└ TODO:` で表示する
- milestones があるタスクは、直近の未完了マイルストーンを `└ MS:` で表示する
- related_meetings があるタスクは、直近の未来の会議を `└ 会議:` で表示する
  - 例: `t-20260401-002 | 賞与考課 | todo | 4/17 | TODO [4/4]`
  - `  └ MS: 面談完了(4/14)`
  - `  └ 会議: 面談(4/14)`

## リマインダー（reminders.json）

- 秘書自身のアクションキュー。「この日になったらこれをやる」を記録する
- 格納場所: `.ai-secretary/global/reminders.json`
- IDは `rem-YYYYMMDD-NNN` 形式で採番（例: rem-20260402-001）
- `action` の種類:
  - `add_to_schedule` — weekly-schedule.json に会議を追加する
  - `notify_user` — ユーザーに情報を伝える
  - `check_and_notify` — 状況を確認してユーザーに報告する
- 処理タイミング: 朝ブリーフィング時に `trigger_date <= 今日` かつ `done == false` のものを実行
- 処理後は `done: true` に更新する
- リマインダーを登録すべきタイミング:
  - 単発会議が決まったとき（該当週の前日にadd_to_schedule）
  - ユーザーが「〇〇忘れないで」と言ったとき（notify_user）
  - waiting中タスクのフォロー期日が来たとき（check_and_notify）
  - PJ中断の解除目安日が来たとき（notify_user）

## 会議ファイルの命名規則

各PJの `meetings/` ディレクトリ内のファイルは以下の命名規則に従う:

- `YYYYMMDD_会議名.vtt` — VTTファイル
- `YYYYMMDD_会議名.txt` — テキストメモ
- `YYYYMMDD_会議名/` — 関連資料がある場合のみディレクトリ化
  - `transcript.vtt`
  - 関連資料ファイル

※ 各PJの `meetings/_NAMING_RULE.md` にも同じルールを記載してある（ユーザーがアップロード時に参照できるよう）

## PJ横断操作

- 全PJのタスクを集計する場合（定期レポート、優先度判断等）、`.ai-secretary/projects/` 配下の全ディレクトリを走査してください
- グローバルの関係者マスタ（`global/people.md`）とPJ固有の関係者（`projects/<PJ>/people.md`）の両方を参照してください
