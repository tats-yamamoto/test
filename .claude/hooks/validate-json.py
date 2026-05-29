"""A1: JSON構文＋構造検証 (PostToolUse)
.ai-secretary/ 配下の JSON 書込み後:
  1) 構文を検証（壊れていれば exit 2 でブロックし、修正を促す）
  2) 主要ファイルの構造ドリフト（必須キー欠落・enum外の値）を非ブロックで警告
hook入力は stdin から JSON で受け取る。
"""
import json
import sys

try:
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

TASK_STATUS = {"todo", "in_progress", "waiting", "suspended", "done"}
DL_TYPE = {"hard", "soft", "asap", "none"}
OBS_KEYS = {"id", "date", "type", "context", "observation", "source"}
OBS_TYPE = {"correction", "preference", "decision", "workflow", "knowledge"}


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return

    tool_input = data.get("tool_input", {}) or {}
    fp = tool_input.get("file_path", "")
    norm = fp.replace("\\", "/")
    if ".ai-secretary/" not in norm or not norm.endswith(".json"):
        return

    # 1) 構文検証（ブロック）
    try:
        with open(fp, "r", encoding="utf-8") as f:
            obj = json.load(f)
    except json.JSONDecodeError as e:
        sys.stderr.write(f"[JSON構文エラー] {norm}: {e}\n即座に修正してください。\n")
        sys.exit(2)
    except FileNotFoundError:
        return
    except Exception:
        return

    # 2) 構造検証（非ブロック警告）
    warns = []

    # 通常タスク（定期タスク daily/weekly/monthly と archive は除外）
    is_recurring = ("/daily/" in norm or "/weekly/" in norm or "/monthly/" in norm)
    if norm.endswith("/tasks.json") and not is_recurring and isinstance(obj, list):
        for t in obj:
            if not isinstance(t, dict):
                continue
            tid = t.get("id", "?")
            for k in ("id", "title", "status"):
                if k not in t:
                    warns.append(f"task {tid}: 必須キー '{k}' 欠落")
            if t.get("status") not in TASK_STATUS:
                warns.append(f"task {tid}: status '{t.get('status')}' が不正")
            dl = t.get("deadline")
            if isinstance(dl, dict) and dl.get("type") not in DL_TYPE:
                warns.append(f"task {tid}: deadline.type '{dl.get('type')}' が不正")

    if norm.endswith("/patterns.json") and isinstance(obj, dict):
        for o in obj.get("observations", []):
            if not isinstance(o, dict):
                continue
            oid = o.get("id", "?")
            miss = OBS_KEYS - set(o.keys())
            if miss:
                warns.append(f"observation {oid}: キー欠落 {sorted(miss)}")
            if o.get("type") not in OBS_TYPE:
                warns.append(f"observation {oid}: type '{o.get('type')}' が不正")

    if warns:
        msg = f"[構造ドリフト警告] {norm}\n- " + "\n- ".join(warns[:10])
        if len(warns) > 10:
            msg += f"\n（他 {len(warns) - 10} 件）"
        print(json.dumps(
            {"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": msg}},
            ensure_ascii=False,
        ))


if __name__ == "__main__":
    main()
