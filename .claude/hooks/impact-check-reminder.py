"""スキル/ルール変更後の impact-check リマインド (PostToolUse)
.claude/skills/ または .claude/rules/ への変更を検出し、影響調査を促す。
発火は自分でシステム（スキル/ルール）を編集した時のみ。
hook入力は stdin から JSON で受け取る。
"""
import json
import sys


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return

    tool_input = data.get("tool_input", {}) or {}
    fp = tool_input.get("file_path", "").replace("\\", "/")

    if ".claude/skills/" in fp or ".claude/rules/" in fp:
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": (
                    "[impact-check] スキル/ルールを変更しました。"
                    "impact-check（EVENT: スキル変更）の実行要否と、data-structure.md の更新要否を確認してください。"
                ),
            }
        }, ensure_ascii=False))


if __name__ == "__main__":
    main()
