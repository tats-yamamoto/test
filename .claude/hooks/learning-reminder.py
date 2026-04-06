"""B1: tasks.json 編集後の learning 記録リマインド (PostToolUse)
tasks.json への書き込みでタスクの完了(done)または取り下げ(drop)を検出した場合、
learning スキルの記録実行を促す。
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

    # .ai-secretary/projects/*/tasks.json のみ対象（定期タスクも含む）
    if ".ai-secretary/" not in file_path or "/tasks.json" not in file_path:
        return

    # 書き込み内容からステータス変更を検出
    content = tool_input.get("new_string", "") or tool_input.get("content", "")

    if '"done"' in content and '"status"' in content:
        print("[learning記録リマインド] タスクの完了を検出しました。")
        print("learning スキルのセクション1（タスク完了時の記録）を実行してください。")
        print("- 所要日数の計算 → patterns.json の accuracy_log に記録")
    elif '"dropped": true' in content or ('"drop_reason"' in content and "null" not in content.split('"drop_reason"')[1][:10]):
        print("[learning記録リマインド] タスクの取り下げを検出しました。")
        print("learning スキルのセクション2（タスク取り下げ時の記録）を実行してください。")
        print("- 取り下げパターン → patterns.json の dropped_task_patterns に記録")

if __name__ == "__main__":
    main()
