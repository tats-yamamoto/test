"""SessionStart: AI秘書の運用ループ詰まり検知（1日1回・問題があるときだけ通知）
チェック内容:
  - .ai-secretary/projects の存在（無ければ /setup 案内）
  - weekly-schedule.json の週番号が今週とズレていないか
  - reminders.json に期限超過の未処理リマインダーがないか
  - patterns.json の observations が滞留していないか（閾値15件）
コスト制御:
  - 実行は1日1回まで（.claude/hooks/.state/health-check.json で管理）
  - 健全なら何も出力しない（コンテキスト注入ゼロ）
"""
import json
import os
import sys
from datetime import date

STATE = os.path.join(".claude", "hooks", ".state", "health-check.json")
OBS_THRESHOLD = 15


def load(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    today = date.today()
    today_s = today.isoformat()

    # 1日1回スロットル（通知の有無に関わらず、その日の初回セッションでのみ実行）
    state = load(STATE) or {}
    if state.get("last_check") == today_s:
        return
    try:
        os.makedirs(os.path.dirname(STATE), exist_ok=True)
        with open(STATE, "w", encoding="utf-8") as f:
            json.dump({"last_check": today_s}, f)
    except Exception:
        pass

    issues = []

    if not os.path.isdir(os.path.join(".ai-secretary", "projects")):
        issues.append(".ai-secretary/projects が見つかりません。/setup で初期セットアップをしてください。")
    else:
        # 週次スケジュールの鮮度
        ws = load(os.path.join(".ai-secretary", "global", "weekly-schedule.json"))
        if isinstance(ws, dict):
            iso = today.isocalendar()
            this_week = f"{iso[0]}-W{iso[1]:02d}"
            if ws.get("week") != this_week:
                issues.append(
                    f"weekly-schedule.json が {ws.get('week')} のまま（今週は {this_week}）。"
                    "meeting スキルの週次リセットが必要です。"
                )
        # 期限超過の未処理リマインダー
        rems = load(os.path.join(".ai-secretary", "global", "reminders.json"))
        if isinstance(rems, list):
            due = [
                r for r in rems
                if not r.get("done") and r.get("trigger_date") and r["trigger_date"] <= today_s
            ]
            if due:
                heads = " / ".join(
                    f"{r.get('trigger_date')} {r.get('description', '')}" for r in due[:3]
                )
                issues.append(f"未処理のリマインダーが{len(due)}件あります（{heads}）。")
        # 暗黙観察の滞留
        pat = load(os.path.join(".ai-secretary", "global", "patterns.json"))
        if isinstance(pat, dict):
            n = len(pat.get("observations", []))
            if n >= OBS_THRESHOLD:
                issues.append(
                    f"暗黙観察が{n}件滞留しています。"
                    "learning スキルのパターン検出（セクション8）の実行を検討してください。"
                )

    if issues:
        msg = (
            "[AI秘書ヘルスチェック（1日1回）]\n- "
            + "\n- ".join(issues)
            + "\nユーザーの依頼を優先しつつ、区切りの良いタイミングで対応を提案してください。"
        )
        print(json.dumps(
            {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": msg}},
            ensure_ascii=True,  # ASCIIエスケープで出力（cp932端末での文字化け防止）
        ))


if __name__ == "__main__":
    main()
