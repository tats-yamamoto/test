"""B2: TODO全完了 + related_meetings 検出 (PostToolUse)
tasks.json への書き込み後、全TODOが完了かつ未来のrelated_meetingsが残っている
タスクを検出し、starts_at の設定を提案する。
hook入力は stdin から JSON で受け取る（Claude Code のhook仕様）。
"""
import json
import sys
from datetime import date


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return

    tool_input = data.get("tool_input", {}) or {}
    file_path = tool_input.get("file_path", "")
    norm = file_path.replace("\\", "/")

    # .ai-secretary/projects/*/tasks.json のみ対象（定期タスクは除外）
    if ".ai-secretary/" not in norm or not norm.endswith("/tasks.json"):
        return
    if "/daily/" in norm or "/weekly/" in norm or "/monthly/" in norm:
        return

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            tasks = json.load(f)
    except Exception:
        return

    if not isinstance(tasks, list):
        return

    today = date.today().isoformat()
    notes = []

    for task in tasks:
        if task.get("status") in ("done", "suspended") or task.get("dropped"):
            continue
        if task.get("starts_at"):
            continue

        todos = task.get("todos", [])
        related_meetings = task.get("related_meetings", [])
        if not todos or not related_meetings:
            continue

        if not all(t.get("status") == "done" for t in todos):
            continue

        future_meetings = [
            m for m in related_meetings if m.get("date") and m["date"] >= today
        ]
        if not future_meetings:
            continue

        next_meeting = min(future_meetings, key=lambda m: m["date"])
        notes.append(
            f"タスク「{task.get('title')}」(ID: {task.get('id')}) は全TODOが完了。"
            f"次の関連会議: {next_meeting.get('title')}({next_meeting.get('date')})。"
            f"starts_at を {next_meeting.get('date')} に設定して会議日まで非表示にすることを提案してください。"
        )

    if notes:
        context = "[TODO全完了検出]\n" + "\n".join(notes)
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": context,
            }
        }, ensure_ascii=False))


if __name__ == "__main__":
    main()
