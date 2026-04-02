---
name: setup
description: 初期セットアップ、PJ追加、情報更新を対話的に行うスキル。ユーザーから業務情報をヒアリングし、ディレクトリ構造とデータファイルを自動生成する。
---

# セットアップスキル

## 3つのモード

### 1. 初回セットアップ（/setup）

`.ai-secretary/` が存在しない、または global/user-profile.md が空の場合に実行。

**ヒアリング順序:**

#### Step 1: ユーザー自身のこと → global/user-profile.md
以下を対話で聞いてください:
- 勤務日・休日（デフォルト: 月〜金勤務、土日休み）
- 勤務時間
- 朝の日課（メール確認、勤怠登録など）
- 会議の隙間時間の使い方（重め/軽めの振り分け）
- 直近のブロック日・休暇予定

#### Step 2: PJ一覧を聞く → ディレクトリ作成
- 「現在関わっているプロジェクトや業務カテゴリを教えてください」
- 回答をもとに `.ai-secretary/projects/<PJ名>/` を作成
- 各PJに tasks.json（空配列）、knowledge.md（テンプレ）、people.md（テンプレ）を生成
- files/, meetings/, archive/, daily/, weekly/, monthly/ も作成
- meetings/ には `_NAMING_RULE.md`（命名規則ファイル）を配置する

#### Step 3: PJごとの詳細 → knowledge.md, people.md
各PJについて以下を聞いてください:
- 背景・目的（ざっくりでOK）
- 現在のフェーズ
- 自分の立場・役割
- 定例会議の曜日・時間・目的・参加者
- 主要な関係者（名前、役職、自分との関係）
- 関係者への頼み方（直接OK / 上司経由 等）
- 知っている制約条件
- その他知っておいてほしいこと

**ヒアリングのコツ:**
- 一度に全部聞かず、PJごとにまとめて聞く
- 「ざっくりで大丈夫です。後から追加・修正できます」と伝える
- 関係者の力関係や好みは、分かる範囲でOK

**定例会議の保存先:**
- 定例会議のヒアリング結果は knowledge.md ではなく `meetings.json` に保存する
- meetings.json の構造は meeting スキル（`.claude/skills/meeting/SKILL.md`）を参照

#### Step 4: グローバル関係者マスタ → global/people.md
- Step 3で出てきた関係者を整理してglobal/people.md に統合

#### Step 5: config.json 生成
- PJ一覧からカテゴリ定義を生成

#### Step 6: 既存タスクの登録
- 「現在抱えているタスクがあればまとめて教えてください」
- テキストで自由に入力してもらい、タスクとして整理・登録

### 2. PJ追加（/setup add-project）

- 新PJ名を聞く
- ディレクトリ作成（tasks.json, knowledge.md, people.md, files/, meetings/, meetings/_NAMING_RULE.md, archive/, daily/, weekly/, monthly/）
- Step 3 と同じ要領でPJ情報をヒアリング
- global/people.md と config.json にも反映

### 3. 情報更新（/setup update <PJ名>）

- 指定PJの現在のknowledge.md, people.md を読み込み
- 「更新したい情報はどれですか？」と聞く
  - フェーズの変更
  - 関係者の追加・変更
  - 制約の追加
  - その他
- 対話で更新内容を確認し、ファイルを更新

## ファイル生成テンプレート

### tasks.json（初期状態）
```json
[]
```

### knowledge.md（初期テンプレ）
```markdown
# <PJ名> ナレッジ

## 背景・目的


## 現在のフェーズ


## 自分の立場


## 定例会議
※ meetings.json で管理

## 決定事項


## 制約


## メモ

```

### people.md（初期テンプレ）
```markdown
# <PJ名> 関係者

```

## 注意事項

- ヒアリングは焦らず、ユーザーのペースで進める
- 「分からない」「後で」と言われたら空欄のまま進める
- すべての入力が終わったら、生成したデータの概要を表示して確認を求める
- 確認OKが出てからファイルを書き込む
