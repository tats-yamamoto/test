# .ai-secretary データ構造

このドキュメントは `.ai-secretary/` 配下の全体構成を定義します。
PJ追加・構造変更時はこのファイルも更新してください。

---

## 全体構成

```
.ai-secretary/
├── global/                          グローバル（PJ横断）データ
│   ├── config.json                  PJ一覧・カテゴリ定義
│   ├── patterns.json                学習パターン（見積もり精度、レビュー傾向等）
│   ├── people.md                    関係者マスタ（全PJ共通）
│   ├── reminders.json               リマインダー（秘書のアクションキュー）
│   ├── user-profile.md              ユーザープロフィール（勤務スタイル、報告ライン等）
│   └── weekly-schedule.json         今週の会議スケジュール
│
├── projects/                        PJ単位のデータ
│   └── <PJ名>/
│       ├── tasks.json               タスク一覧
│       ├── knowledge.md             ナレッジ（背景・経緯・決定事項・行間情報）
│       ├── people.md                関係者（PJ固有の役職・力関係・レビュー傾向）
│       ├── meetings.json            定例会議の定義
│       ├── meetings/                会議VTT・メモ・関連資料
│       │   └── _NAMING_RULE.md      命名規則（ユーザー参照用）
│       ├── files/                   PJ関連ファイル・資料
│       ├── daily/                   定期タスク（日次）
│       │   └── tasks.json
│       ├── weekly/                  定期タスク（週次）
│       │   └── tasks.json
│       ├── monthly/                 定期タスク（月次）
│       │   └── tasks.json
│       └── archive/                 アーカイブ（完了済み・古いデータ）
│
├── templates/                       ドラフト用テンプレート
│   ├── email-internal.md            社内メール
│   ├── proposal.md                  報告書・提案書
│   ├── minutes.md                   議事録
│   └── weekly-report.md             週報
│
└── archive/                         グローバルアーカイブ
```

---

## 各ファイルの詳細

### global/config.json

PJ一覧とタスクカテゴリの定義。

```json
{
  "projects": ["PJ名1", "PJ名2", ...],
  "categories": ["報告・資料作成", "開発・PoC", ...]
}
```

- PJ追加時は setup スキルがここにも追記する
- categories はタスク追加時のカテゴリ推定に使用

### global/patterns.json

学習データの蓄積。全スキルが参照・更新する。

```json
{
  "time_estimation": {
    "accuracy_log": [
      { "task_id": "t-...", "title": "...", "category": "...", "created_at": "YYYY-MM-DD", "completed_at": "YYYY-MM-DD", "days": N }
    ]
  },
  "task_decomposition": [],
  "priority_tendencies": {
    "observations": [
      { "date": "YYYY-MM-DD", "original": "...", "corrected": "...", "context": "..." }
    ]
  },
  "dropped_task_patterns": {
    "observations": []
  },
  "recurring_tasks": [],
  "review_tendencies": {
    "by_reviewer": {
      "<レビュアー名>": { "total_reviews": N, "common_points": ["..."], "last_review": "YYYY-MM-DD" }
    }
  },
  "planning_history": {
    "observations": []
  }
}
```

| セクション | 主に使うスキル | 内容 |
|---|---|---|
| time_estimation | learning | タスク完了時の所要日数実績 |
| task_decomposition | planning | タスク分解パターン |
| priority_tendencies | prioritization, learning | ユーザーの優先度修正履歴 |
| dropped_task_patterns | learning | 取り下げタスクの傾向 |
| recurring_tasks | learning | 繰り返しタスクの検出結果 |
| review_tendencies | learning, self-review | レビュアーごとの指摘傾向（定量） |
| planning_history | planning | 段取りの実績記録 |
| observations | learning（全エージェントが記録） | 会話中の暗黙観察ログ |
| insights | learning（morning-briefingが検出） | 観察から検出されたパターン（信頼度スコア付き） |

#### observations のエントリ

```json
{
  "id": "obs-YYYYMMDD-NNN",
  "date": "YYYY-MM-DD",
  "source": "スキル名またはエージェント名",
  "type": "correction | preference | decision | workflow",
  "description": "何が起きたかの簡潔な記述",
  "context": "どういう状況で起きたか"
}
```

- `correction`: 秘書の提案をユーザーが修正した
- `preference`: ユーザーの好み・スタイルが現れた
- `decision`: 複数選択肢からの選択
- `workflow`: 作業手順・順序のパターン
- `knowledge`: PJ・関係者に関する暗黙知（人の傾向、暗黙のルール、力関係等）

#### insights のエントリ

```json
{
  "id": "ins-YYYYMMDD-NNN",
  "created_at": "YYYY-MM-DD",
  "updated_at": "YYYY-MM-DD",
  "confidence": 0.3,
  "description": "行動パターンの言語化",
  "evidence": ["obs-YYYYMMDD-NNN"],
  "domain": "drafting | prioritization | planning | communication | workflow | scheduling",
  "status": "active | crystallized | dismissed"
}
```

- 信頼度 0.3（初検出）→ 0.9（確立）の範囲で変動
- `crystallized`: スキル・ルールに反映済み
- `dismissed`: ユーザーが明示的に否定

### global/people.md

全PJ共通の関係者マスタ。PJ固有の情報は各PJの people.md に記載。

```markdown
# 関係者マスタ（組織共通）

## <名前>
- 役職:
- 関係:
- 頼み方:
- 備考:
```

### global/reminders.json

秘書のアクションキュー。朝ブリーフィング時に処理される。

```json
[
  {
    "id": "rem-YYYYMMDD-NNN",
    "trigger_date": "YYYY-MM-DD",
    "action": "add_to_schedule | notify_user | check_and_notify",
    "description": "概要",
    "details": { ... },
    "related_task": "t-... or null",
    "done": false
  }
]
```

| action | 処理内容 |
|---|---|
| add_to_schedule | weekly-schedule.json に会議を追加 |
| notify_user | ユーザーにメッセージを伝える |
| check_and_notify | 状況を確認して報告 |

### global/user-profile.md

ユーザーの勤務スタイル・報告ライン。全エージェントが参照。

```markdown
# ユーザープロフィール

## 所属
## 勤務スタイル
## 朝の日課
## 隙間時間の使い方
## 報告ライン
```

### global/weekly-schedule.json

今週の会議スケジュール。月曜朝に meeting スキルが定例から自動生成。

```json
{
  "week": "YYYY-Www",
  "generated_from_recurring": true,
  "meetings": [
    {
      "id": "ws-NNN",
      "source_id": "mtg-r-NNN or null",
      "title": "会議名",
      "date": "YYYY-MM-DD",
      "time": "HH:MM-HH:MM",
      "participants": ["名前"],
      "purpose": "目的",
      "project": "PJ名",
      "status": "scheduled | rescheduled | cancelled",
      "note": "備考 or null"
    }
  ]
}
```

---

### projects/\<PJ\>/tasks.json

タスク一覧。配列形式。

```json
[
  {
    "id": "t-YYYYMMDD-NNN",
    "title": "タスク名",
    "status": "todo | in_progress | waiting | done",
    "deadline": {
      "date": "YYYY-MM-DD or null",
      "type": "hard | soft | asap | none",
      "note": "補足"
    },
    "context": {
      "source": "meeting | chat | email | self",
      "source_detail": "発生元の詳細",
      "requester": "依頼者名",
      "approver": "承認者名",
      "background": "背景・経緯",
      "behind_the_scenes": "行間情報",
      "related_files": [],
      "constraints": "制約条件"
    },
    "milestones": [
      { "title": "MS名", "date": "YYYY-MM-DD", "status": "todo | in_progress | done" }
    ],
    "review_history": [
      { "reviewer": "名前", "date": "YYYY-MM-DD", "feedback": "内容", "resolved": false }
    ],
    "starts_at": "YYYY-MM-DD or null",
    "tags": [],
    "created_at": "ISO8601",
    "updated_at": "ISO8601",
    "completed_at": "ISO8601 or null",
    "dropped": false,
    "drop_reason": null
  }
]
```

### projects/\<PJ\>/knowledge.md

PJのナレッジ。決定事項には行間情報を添える。

```markdown
# <PJ名> ナレッジ

## 背景・目的
## 現在のフェーズ
## 自分の立場
## 定例会議
※ meetings.json で管理
## 決定事項
- YYYY-MM-DD <会議名>: <決定内容>
  - 【行間】<VTTに残らない補足>
## 制約
## メモ
```

### projects/\<PJ\>/people.md

PJ固有の関係者情報。レビュー傾向は日付付きで蓄積。

```markdown
# <PJ名> 関係者

## <名前>
- 役職:
- 自分との関係:
- 頼み方:
- レビュー傾向:
  - YYYY-MM-DD: <FB内容> → <傾向の分析>
- スケジュール:
```

### projects/\<PJ\>/meetings.json

定例会議の定義。weekly-schedule.json への展開元。

```json
[
  {
    "id": "mtg-r-{PJ略称}-NNN",
    "title": "会議名",
    "day_of_week": "mon | tue | wed | thu | fri | daily",
    "time": "HH:MM-HH:MM",
    "participants": ["名前"],
    "purpose": "目的",
    "project": "PJ名",
    "suspended": false,
    "suspended_reason": "理由 or null"
  }
]
```

- `day_of_week: "daily"` は週次リセット時に月〜金の全日に展開される
- `suspended: true` の定例は週次リセット時にスキップされる（PJ中断時に使用）

### projects/\<PJ\>/meetings/

会議VTT・メモ・関連資料の格納先。命名規則は `_NAMING_RULE.md` を参照。

```
meetings/
├── _NAMING_RULE.md
├── YYYYMMDD_会議名.vtt
├── YYYYMMDD_会議名.txt
└── YYYYMMDD_会議名/          ← 関連資料がある場合のみ
    ├── transcript.vtt
    └── 資料.pdf
```

### projects/\<PJ\>/daily/ weekly/ monthly/

定期タスク。通常タスクとは別管理。completion_log で完了を記録。

```json
[
  {
    "id": "t-YYYYMMDD-NNN",
    "title": "タスク名",
    "description": "説明",
    "cycle_day": "mon",
    "cycle_date": "last",
    "completion_log": [
      { "period": "YYYY-MM-DD | YYYY-Www | YYYY-MM", "completed_at": "YYYY-MM-DD" }
    ]
  }
]
```

- 日次: period = `YYYY-MM-DD`（直近30日分のみ保持）
- 週次: period = `YYYY-Www`（**提出先サイクルの週番号**。例: W15月曜の報告会で発表する週報 → period = W15）
- 月次: period = `YYYY-MM`（**提出先サイクルの月**）

#### サイクル基準日（cycle_day / cycle_date）

週次・月次タスクには、そのタスクの「提出先サイクル」を特定するための基準日を設定する。ブリーフィング時の完了判定に使用。

| フィールド | 対象 | 値 | 意味 |
|---|---|---|---|
| `cycle_day` | 週次 | `"mon"` 〜 `"fri"` | サイクルの基準曜日。次のこの曜日が属するISO週 = チェック対象period |
| `cycle_date` | 月次 | `1`〜`28` or `"last"` | サイクルの基準日。この日を過ぎたら来月がチェック対象period |

- 未設定の場合: 週次は今週、月次は今月をチェック（従来互換）
- 例: 週報（cycle_day: "mon"）→ 木曜時点では「次の月曜のISO週」をチェック → まだ未完了なら表示

### templates/

ドラフトエージェントが使用するテンプレート。必要に応じて追加。

---

## ID採番規則

| 対象 | 形式 | 例 |
|---|---|---|
| タスク | `t-YYYYMMDD-NNN` | t-20260402-001 |
| リマインダー | `rem-YYYYMMDD-NNN` | rem-20260402-001 |
| 定例会議 | `mtg-r-{PJ略称}-NNN` | mtg-r-cb-001 |
| 週次スケジュール | `ws-NNN` | ws-001 |

---

## 関係するスキル・ルール

| データ | 主に管理するスキル |
|---|---|
| tasks.json | task-manager |
| knowledge.md, people.md | knowledge-base |
| meetings.json, weekly-schedule.json | meeting |
| patterns.json | learning, planning, prioritization, self-review |
| reminders.json | secretary エージェント（morning-briefing で処理） |
| templates/ | drafter エージェント |
| config.json | setup |
| 構成変更の影響調査 | impact-check |

データ取扱いの詳細ルールは `.claude/rules/data-handling.md` を参照。
