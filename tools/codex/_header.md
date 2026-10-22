<!--
  ⚠ このファイル（AGENTS.md）は自動生成です。直接編集しないでください（次回の同期で上書きされます）。
  正本: .claude/CLAUDE.md / .claude/rules/*.md / .claude/skills/ / .claude/commands/ / tools/codex/*.md
  再生成: python tools/sync-codex.py
-->

# Codex で動かすときの補足

この秘書の設定は Claude Code 用に書かれたものを、Codex でも使えるように変換したものです。以下の読み替えをしてください。

- **スキル**: `.agents/skills/` にあります（`.claude/skills/` と同じ内容のコピー）。本文中の「スキル（`.claude/skills/`）」はどちらを読んでもかまいません。
- **ルール**: 本文中で「`.claude/rules/` を参照」とあるルールは、このファイルの末尾に全文を収録済みです。
- **ツール名**: スキル・ルール中の `Read` / `Write` / `Edit` / `Grep` / `Bash` などは Claude Code の道具の名前です。Codex では同じ働きをするファイル操作・シェル操作に読み替えてください。
- **現在時刻**: 依頼ごとにフックが「現在: 日時」を渡します。届いていないときは、シェルで日時を確認してから、スケジュールや優先度の提案をしてください。
- **正本の編集**: スキル・ルールを直すときは、必ず `.claude/` 側の正本を編集してください。`AGENTS.md` と `.agents/skills/` は編集しません。編集後にフックが自動で同期します。動かなかったときは `python tools/sync-codex.py` を実行してください。
- **スラッシュコマンド**: Codex には、このプロジェクト用のコマンド機能がありません。ユーザーが下の表の言葉（例: `/morning`、`morning`）を使ったら、対応するファイルを開いて、その指示に従ってください。`$ARGUMENTS` は、ユーザーが続けて書いた内容に置き換えます。

{{COMMANDS}}
