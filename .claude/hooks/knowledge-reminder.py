"""B2: 操作前のナレッジ・関係者参照リマインド (PreToolUse)
tasks.json を編集する前に、同PJの knowledge.md と people.md を
読み込んだか確認を促す。ブロックはしない（常に exit 0）。
"""
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

def main():
    tool_input_raw = os.environ.get("CLAUDE_TOOL_INPUT", "{}")
    try:
        tool_input = json.loads(tool_input_raw)
    except json.JSONDecodeError:
        return

    file_path = tool_input.get("file_path", "").replace("\\", "/")

    # .ai-secretary/projects/<PJ>/tasks.json のみ対象
    if ".ai-secretary/projects/" not in file_path or "/tasks.json" not in file_path:
        return

    # PJ名を抽出
    match = re.search(r"\.ai-secretary/projects/([^/]+)/", file_path)
    pj_name = match.group(1) if match else "該当PJ"

    print(f"[ナレッジ参照リマインド] {pj_name} の tasks.json を編集しようとしています。")
    print(f"同PJの knowledge.md と people.md は読み込み済みですか？")
    print(f"未読の場合は先に参照してください。")

if __name__ == "__main__":
    main()
