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
  - 【行間】<VTTに残らない補足。誰が駆動したか・決定権者のサイン有無など>

## 論点・検討中
- YYYY-MM-DD <会議名>: <まだ決まっていない論点・方向性>
  - 【行間】<同意の質（本物の合意か、忖度・ノリ・沈黙か）・駆動者・本心未確認など>

## 制約
- （制約条件のリスト）

## メモ
- （その他の重要な情報）
```

### 決定事項と論点・検討中の書き分け

`core-principles.md`「発散と収束の区別」に従い、確度で書き先を分ける:

- **決定**（明示的クローズ・担当/期限確定・決定権者のクローズあり）→ `## 決定事項`
- **検討中／論点**（発散・表面同意のみ・結論なし）→ `## 論点・検討中`
- 曖昧なものは決定に倒さず、ユーザーに確認してから書く

**ライフサイクル**: 論点が後で実際に決まったら、`## 論点・検討中` から該当行を消し、**決まった日付**で `## 決定事項` に移す（「いつ決まったか」を正しく残すため）。

## people.md の構造（PJ単位）

```markdown
# <PJ名> 関係者

## <名前>
- 役職: 
- 自分との関係: 
- このPJでの役割・力関係: 
- 頼み方: 
- スケジュール: 
```

※ **レビュー傾向**（その人が成果物をどう評価・指摘するか）は people.md ではなく **`.ai-secretary/global/review/people/<名前>.md`** に一元管理する。people.md は「人の基本情報（global/people.md）」と「そのPJでの役割・力関係（PJ単位）」を担う。

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

## 蓄積されたナレッジ観察からの更新提案

朝ブリーフィング時に、`patterns.json` の `observations`（type: `knowledge`）を確認し、蓄積された暗黙知を knowledge.md / people.md に反映する提案を行う。

### 手順

1. `patterns.json` の `observations` から `type: "knowledge"` のエントリを抽出する
2. PJごとにグループ化する（`context` からPJ名を判定）
3. 各PJの既存の knowledge.md / people.md を読み込み、重複がないか確認する
4. 重複しない新情報がある場合、追記案をユーザーに提示する:

```
📝 ナレッジ更新の提案

最近の会話から以下の情報を拾いました:

【CodeBeamer / people.md】
- シンカイさん: 提案資料は箇条書きより文章形式を好む傾向（4/2, 4/5 の会話から）

【直接業務 / knowledge.md メモ欄】
- 部内の報告書レビューは金曜午前に集中する傾向がある（4/1, 4/3, 4/4 の会話から）

追記しますか？（個別に選択可能）
```

5. ユーザーが承認した分のみ追記する
6. 追記完了後、該当の observation を `observations` 配列から削除する

### knowledge タイプの insight への昇華

同じ人物・PJに関する knowledge 観察が繰り返し出てくる場合、learning スキルのパターン検出（セクション8）で insight に昇華される。例:

- 「シンカイさんは文章形式を好む」が3回観察 → insight（confidence: 0.7）
- → 結晶化提案: 「people.md の シンカイさん の 頼み方 に『提案資料は文章形式で』を追記しませんか？」

このように、蓄積型ナレッジも暗黙観察→気づき→結晶化のパイプラインに乗る。

## 会議関連の情報

会議の定例・スケジュールに関する情報は knowledge.md ではなく以下を参照すること:
- 定例会議の定義: `.ai-secretary/projects/<PJ>/meetings.json`
- 今週のスケジュール: `.ai-secretary/global/weekly-schedule.json`

knowledge.md の「## 定例会議」セクションは「※ meetings.json で管理」とだけ記載し、会議の詳細は meetings.json に集約する。
