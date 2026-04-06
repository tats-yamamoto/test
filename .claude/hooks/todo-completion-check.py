"""B2: TODO全完了 + related_meetings 検出 (PostToolUse)
tasks.json への書き込み後、全TODOが完了かつ未来のrelated_meetingsが残っている
タスクを検出し、starts_at の設定を提案する。
"""
import json
import os
import sys
from datetime import date

sys.stdout.reconfigure(encoding="utf-8")


def main():
    tool_input_raw = os.environ.get("CLAUDE_TOOL_INPUT", "{}")
    try:
        tool_input = json.loads(tool_input_raw)
    except json.JSONDecodeError:
        return

    file_path = tool_input.get("file_path", "").replace("\\", "/")

    # .ai-secretary/projects/*/tasks.json のみ対象（定期タスクは除外）
    if ".ai-secretary/" not in file_path or not file_path.endswith("/tasks.json"):
        return
    if "/daily/" in file_path or "/weekly/" in file_path or "/monthly/" in file_path:
        return

    # ファイルを読み込んでチェック
    actual_path = tool_input.get("file_path", "")
    try:
        with open(actual_path, "r", encoding="utf-8") as f:
            tasks = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError, Exception):
        return

    today = date.today().isoformat()

    for task in tasks:
        # 完了・取り下げ・中断タスクはスキップ
        if task.get("status") == "done" or task.get("dropped") or task.get("status") == "suspended":
            continue

        # 既に starts_at が設定されているタスクはスキップ
        if task.get("starts_at"):
            continue

        todos = task.get("todos", [])
        related_meetings = task.get("related_meetings", [])

        # TODOがない、またはrelated_meetingsがないタスクはスキップ
        if not todos or not related_meetings:
            continue

        # 全TODOが完了しているか
        all_done = all(t.get("status") == "done" for t in todos)
        if not all_done:
            continue

        # 未来のrelated_meetingsがあるか
        future_meetings = [
            m for m in related_meetings
            if m.get("date") and m["date"] >= today
        ]
        if not future_meetings:
            continue

        # 最も近い未来の会議
        next_meeting = min(future_meetings, key=lambda m: m["date"])

        print(f"[TODO全完了検出] タスク「{task['title']}」(ID: {task['id']}) の全TODOが完了しています。")
        print(f"次の関連会議: {next_meeting['title']}({next_meeting['date']})")
        print(f"starts_at を {next_meeting['date']} に設定して、会議日まで非表示にすることを提案してください。")


if __name__ == "__main__":
    main()
