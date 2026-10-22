"""フック共通: 入力の読み取り（Claude Code / Codex の両対応）

PostToolUse の入力から「どのファイルを、どんな内容で編集したか」を取り出す。
  - Claude Code: tool_input.file_path と new_string / content
  - Codex: tool_name=apply_patch で、tool_input.command にパッチ本文が入る
    （パッチの「*** Add/Update/Delete File: <パス>」行からパスを読む。
      書式は公式ドキュメントに詳細がないため、Codex 導入時に実データで要確認）
"""
import json
import os
import re
import sys

_PATCH_FILE = re.compile(r"^\*\*\* (?:Add|Update|Delete) File: (.+?)\s*$")
_PATCH_MOVE = re.compile(r"^\*\*\* Move to: (.+?)\s*$")


def read_stdin():
    """stdin の JSON を読む。読めなければ None。"""
    try:
        return json.load(sys.stdin)
    except Exception:
        return None


def _patch_text(tool_input):
    cmd = tool_input.get("command", "")
    if isinstance(cmd, list):
        # ["apply_patch", "<patch>"] のような配列形式にも備える
        cmd = "\n".join(str(c) for c in cmd)
    return cmd if isinstance(cmd, str) else ""


def _parse_patch(text, cwd):
    """パッチ本文を [{"path", "content"}] に分解する。content は追加行(+)のみ。"""
    edits = []
    cur = None
    for line in text.splitlines():
        m = _PATCH_FILE.match(line) or _PATCH_MOVE.match(line)
        if m:
            path = m.group(1).strip().strip('"')
            if cwd and not os.path.isabs(path):
                path = os.path.join(cwd, path)
            cur = {"path": path, "content": ""}
            edits.append(cur)
            continue
        if cur is not None and line.startswith("+") and not line.startswith("+++"):
            cur["content"] += line[1:] + "\n"
    return edits


def get_edits(data):
    """編集されたファイルの一覧を返す: [{"path": 実パス, "norm": /区切り, "content": 書いた内容}]"""
    if not isinstance(data, dict):
        return []
    tool_input = data.get("tool_input", {}) or {}
    if not isinstance(tool_input, dict):
        return []

    edits = []
    fp = tool_input.get("file_path", "")
    if fp:
        # Claude Code 形式（従来どおり）
        content = tool_input.get("new_string", "") or tool_input.get("content", "") or ""
        edits.append({"path": fp, "content": content})
    elif data.get("tool_name") == "apply_patch" or "*** Begin Patch" in _patch_text(tool_input):
        # Codex 形式
        edits = _parse_patch(_patch_text(tool_input), data.get("cwd", ""))

    for e in edits:
        e["norm"] = e["path"].replace("\\", "/")
    return edits


def emit_context(event, msg):
    """モデルへの追加コンテキストを出力する（Claude Code / Codex 共通の JSON 形式）。"""
    print(json.dumps(
        {"hookSpecificOutput": {"hookEventName": event, "additionalContext": msg}},
        ensure_ascii=True,  # ASCIIエスケープで出力（cp932端末での文字化け防止）
    ))
