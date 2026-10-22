"""PostToolUse: 正本（.claude/ のスキル・ルール・CLAUDE.md・コマンド）を編集したら、
Codex 用ファイル（AGENTS.md / .agents/skills/）を自動で作り直す。
Claude Code / Codex のどちらで編集しても動く（_hookio 参照）。
"""
import importlib.util
import os

from _hookio import emit_context, get_edits, read_stdin

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WATCH = (".claude/CLAUDE.md", ".claude/rules/", ".claude/skills/", ".claude/commands/", "tools/codex/")


def main():
    data = read_stdin()
    if not any(w in e["norm"] for e in get_edits(data) for w in WATCH):
        return

    spec = importlib.util.spec_from_file_location("sync_codex", os.path.join(ROOT, "tools", "sync-codex.py"))
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
        changes, size, warn = mod.sync()
    except Exception as ex:
        emit_context("PostToolUse", f"[Codex同期] 失敗しました: {ex}。python tools/sync-codex.py を手動で実行してください。")
        return

    msgs = []
    if changes:
        msgs.append(f"[Codex同期] AGENTS.md / .agents/skills/ を更新しました（{len(changes)} 件）。")
    if warn:
        msgs.append("[Codex同期・警告] " + warn)
    if msgs:
        emit_context("PostToolUse", "\n".join(msgs))


if __name__ == "__main__":
    main()
