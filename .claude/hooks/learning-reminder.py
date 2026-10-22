"""完了/取下げ時の学習記録リマインド (PostToolUse)
tasks.json への書き込みで done / drop を検出したら、learning スキルの記録を促す。
発火は完了・取り下げ時のみ（通常の追加・更新では鳴らない）。
※ milestones の "done": false や status enum の列挙にマッチしないよう、
  "status": "done" / "dropped": true の形のみを検出する。
hook入力は stdin から JSON で受け取る（Claude Code / Codex 両対応: _hookio 参照）。
"""
import re

from _hookio import emit_context, get_edits, read_stdin


def main():
    data = read_stdin()
    for e in get_edits(data):
        if check(e["norm"], e["content"]):
            return  # 1回の編集で通知は1回まで


def check(fp, content):
    if ".ai-secretary/" not in fp or not fp.endswith("/tasks.json"):
        return False

    msg = None
    if re.search(r'"status"\s*:\s*"done"', content):
        msg = "タスク完了を検出。learning スキル §1（完了時記録: 所要日数→accuracy_log、MS実績→planning_history）を実行し、archive 移動も忘れずに。"
    elif re.search(r'"dropped"\s*:\s*true', content):
        msg = "タスク取り下げを検出。learning スキル §2（取り下げ傾向→dropped_task_patterns）を実行し、archive 移動も忘れずに。"

    if msg:
        emit_context("PostToolUse", "[学習記録リマインド] " + msg)
        return True
    return False


if __name__ == "__main__":
    main()
