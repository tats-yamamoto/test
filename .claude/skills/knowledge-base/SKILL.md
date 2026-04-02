---
name: knowledge-base
description: ナレッジベースの参照・更新を行うスキル。PJの背景・経緯・決定事項・行間情報、および関係者情報の読み込み・追記手順を定義する。
---

# ナレッジベース参照・更新スキル

## データの場所

- PJナレッジ: `.ai-secretary/projects/<PJ名>/knowledge.md`
- PJ関係者: `.ai-secretary/projects/<PJ名>/people.md`
- グローバル関係者: `.ai-secretary/global/people.md`
- VTT・議事録: `.ai-secretary/projects/<PJ名>/meetings/`
- 関連ファイル: `.ai-secretary/projects/<PJ名>/files/`

## knowledge.md の構造

```markdown
# <PJ名> ナレッジ

## 背景・目的
（PJの概要、目的）

## 現在のフェーズ
（現在の状況）

## 自分の立場
（このPJでの自分の役割）

## 定例会議
※ meetings.json で管理

## 決定事項
- YYYY-MM-DD <会議名>: <決定内容>
  - 【行間】<VTTに残らない補足>

## 制約
- （制約条件のリスト）

## メモ
- （その他の重要な情報）
```

## people.md の構造（PJ単位）

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

## 参照の手順

1. タスクやPJ名が特定できたら、該当PJの knowledge.md と people.md を読み込む
2. 関係者名が出たら、PJ単位の people.md とグローバルの people.md の両方を確認
3. 「行間」情報（behind_the_scenes）は特に注意して参照する

## 更新の手順

1. 更新内容をユーザーに提示し、承認を得る
2. 既存の構造を壊さないように追記する
3. 日付を必ず付与する
4. 新しいセクションが必要な場合は、既存の見出しレベルに合わせる

## 新規情報の検出と提案

VTT/テキスト抽出時に以下を検出したら、ナレッジ追加を提案する:

- 新しい決定事項
- 新しい制約・方針変更
- 新しい関係者（名前、役職が分かれば記録）
- 新しい用語（knowledge.md のメモに追記）

## 会議関連の情報

会議の定例・スケジュールに関する情報は knowledge.md ではなく以下を参照すること:
- 定例会議の定義: `.ai-secretary/projects/<PJ>/meetings.json`
- 今週のスケジュール: `.ai-secretary/global/weekly-schedule.json`

knowledge.md の「## 定例会議」セクションは「※ meetings.json で管理」とだけ記載し、会議の詳細は meetings.json に集約する。
