"""スキル/ルール変更後の impact-check リマインド (PostToolUse)
.claude/skills/ または .claude/rules/ への変更を検出し、影響調査を促す。
発火は自分でシステム（スキル/ルール）を編集した時のみ。
Codex 用の生成物（.agents/skills/）を直接編集した場合は、正本で直すよう促す。
hook入力は stdin から JSON で受け取る（Claude Code / Codex 両対応: _hookio 参照）。
"""
from _hookio import emit_context, get_edits, read_stdin


def main():
    data = read_stdin()
    paths = [e["norm"] for e in get_edits(data)]

    if any(".claude/skills/" in fp or ".claude/rules/" in fp for fp in paths):
        emit_context(
            "PostToolUse",
            "[impact-check] スキル/ルールを変更しました。"
            "impact-check（EVENT: スキル変更）の実行要否と、data-structure.md の更新要否を確認してください。",
        )
    elif any(".agents/skills/" in fp or fp.endswith("/AGENTS.md") or fp == "AGENTS.md" for fp in paths):
        emit_context(
            "PostToolUse",
            "[注意] AGENTS.md と .agents/skills/ は .claude/ から自動生成されるファイルです（次回の同期で上書きされます）。"
            "同じ変更を正本（.claude/CLAUDE.md・.claude/rules/・.claude/skills/）に入れてから、"
            "python tools/sync-codex.py を実行してください。",
        )


if __name__ == "__main__":
    main()
