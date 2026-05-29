"""完了/取下げ時の学習記録リマインド (PostToolUse)
tasks.json への書き込みで done / drop を検出したら、learning スキルの記録を促す。
発火は完了・取り下げ時のみ（通常の追加・更新では鳴らない）。
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
    if ".ai-secretary/" not in fp or not fp.endswith("/tasks.json"):
        return

    content = tool_input.get("new_string", "") or tool_input.get("content", "") or ""

    msg = None
    if '"done"' in content and '"status"' in content:
        msg = "タスク完了を検出。learning スキル §1（完了時記録: 所要日数→accuracy_log、MS実績→planning_history）を実行し、archive 移動も忘れずに。"
    elif '"dropped": true' in content:
        msg = "タスク取り下げを検出。learning スキル §2（取り下げ傾向→dropped_task_patterns）を実行し、archive 移動も忘れずに。"

    if msg:
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": "[学習記録リマインド] " + msg,
            }
        }, ensure_ascii=False))


if __name__ == "__main__":
    main()
