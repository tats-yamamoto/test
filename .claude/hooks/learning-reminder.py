"""完了/取下げ時の学習記録リマインド (PostToolUse)
tasks.json への書き込みで done / drop を検出したら、learning スキルの記録を促す。
発火は完了・取り下げ時のみ（通常の追加・更新では鳴らない）。
※ milestones の "done": false や status enum の列挙にマッチしないよう、
  "status": "done" / "dropped": true の形のみを検出する。
hook入力は stdin から JSON で受け取る。
"""
import json
import re
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
    if re.search(r'"status"\s*:\s*"done"', content):
        msg = "タスク完了を検出。learning スキル §1（完了時記録: 所要日数→accuracy_log、MS実績→planning_history）を実行し、archive 移動も忘れずに。"
    elif re.search(r'"dropped"\s*:\s*true', content):
        msg = "タスク取り下げを検出。learning スキル §2（取り下げ傾向→dropped_task_patterns）を実行し、archive 移動も忘れずに。"

    if msg:
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": "[学習記録リマインド] " + msg,
            }
        }, ensure_ascii=True))  # ASCIIエスケープで出力（cp932端末での文字化け防止）


if __name__ == "__main__":
    main()
