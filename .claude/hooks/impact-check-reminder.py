"""A2: スキル/ルール変更後の impact-check リマインド (PostToolUse)
.claude/skills/ または .claude/rules/ への変更を検出し、
impact-check スキルの実行と data-structure.md の更新確認を促す。
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

def main():
    tool_input_raw = os.environ.get("CLAUDE_TOOL_INPUT", "{}")
    try:
        tool_input = json.loads(tool_input_raw)
    except json.JSONDecodeError:
        return

    file_path = tool_input.get("file_path", "").replace("\\", "/")

    if ".claude/skills/" in file_path or ".claude/rules/" in file_path:
        print("[impact-check必須] スキル/ルールを変更しました。")
        print("1. impact-check スキル（EVENT: スキル変更）を実行してください")
        print("2. data-structure.md の更新が必要か確認してください")

if __name__ == "__main__":
    main()
