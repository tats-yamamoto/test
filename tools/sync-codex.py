"""Codex 用ファイルを .claude/ から生成する

正本（手で編集するのはこちらだけ）:
  .claude/CLAUDE.md, .claude/rules/*.md, .claude/skills/, .claude/commands/, tools/codex/*.md
生成物（編集しない。毎回上書きされる）:
  AGENTS.md        … CLAUDE.md ＋ ルール全文（Codex は別ファイルを自動で読まないため埋め込む）
  .agents/skills/  … .claude/skills/ のコピー

CLAUDE.md 内の Claude 専用ブロック:
  <!-- claude-only:start NAME -->
  ...
  <!-- claude-only:end -->
  は、tools/codex/NAME.md があればその内容に、なければ削除して AGENTS.md に出力する。

使い方:
  python tools/sync-codex.py          生成する
  python tools/sync-codex.py --check  生成物が古ければ終了コード1（書き込まない）
"""
import filecmp
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLAUDE_DIR = os.path.join(ROOT, ".claude")
CODEX_TPL = os.path.join(ROOT, "tools", "codex")
AGENTS_MD = os.path.join(ROOT, "AGENTS.md")
SKILLS_SRC = os.path.join(CLAUDE_DIR, "skills")
SKILLS_DST = os.path.join(ROOT, ".agents", "skills")
CODEX_CONFIG = os.path.join(ROOT, ".codex", "config.toml")


def _size_limit():
    """AGENTS.md の読み込み上限。.codex/config.toml の project_doc_max_bytes、なければ標準の32KiB。"""
    try:
        m = re.search(r"^\s*project_doc_max_bytes\s*=\s*(\d+)", _read(CODEX_CONFIG), re.M)
        if m:
            return int(m.group(1))
    except OSError:
        pass
    return 32 * 1024

# 印は行頭にあるものだけ認識する（説明文中に書かれた印を誤認しないため）
BLOCK = re.compile(
    r"^<!-- claude-only:start (\S+) -->\n(.*?)^<!-- claude-only:end -->\n?", re.S | re.M
)


def _read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def _tpl(name):
    path = os.path.join(CODEX_TPL, name + ".md")
    return _read(path) if os.path.exists(path) else ""


def _commands_table():
    """Claude のスラッシュコマンド一覧（Codex にはプロジェクト単位のコマンドがないため対応表を載せる）"""
    cdir = os.path.join(CLAUDE_DIR, "commands")
    rows = []
    for fn in sorted(os.listdir(cdir)) if os.path.isdir(cdir) else []:
        if not fn.endswith(".md"):
            continue
        m = re.search(r"^description:\s*(.+)$", _read(os.path.join(cdir, fn)), re.M)
        desc = m.group(1).strip().strip('"') if m else ""
        rows.append(f"| `/{fn[:-3]}` | {desc} | `.claude/commands/{fn}` |")
    if not rows:
        return ""
    return "| 言われた言葉 | 内容 | 従う指示 |\n|---|---|---|\n" + "\n".join(rows) + "\n"


def build_agents_md():
    body = BLOCK.sub(lambda m: _tpl(m.group(1)), _read(os.path.join(CLAUDE_DIR, "CLAUDE.md")))
    header = _tpl("_header").replace("{{COMMANDS}}", _commands_table())

    parts = [header.rstrip() + "\n", body.strip() + "\n"]
    rdir = os.path.join(CLAUDE_DIR, "rules")
    for fn in sorted(os.listdir(rdir)):
        if fn.endswith(".md"):
            parts.append(
                f"<!-- 以下は .claude/rules/{fn} の全文（自動収録） -->\n\n"
                + _read(os.path.join(rdir, fn)).strip() + "\n"
            )
    return "\n---\n\n".join(parts)


def _skill_files(base):
    out = set()
    for d, _, files in os.walk(base):
        for fn in files:
            out.add(os.path.relpath(os.path.join(d, fn), base).replace(os.sep, "/"))
    return out


def plan_skills():
    """(コピーが必要なファイル, 削除が必要なファイル)"""
    src = _skill_files(SKILLS_SRC)
    dst = _skill_files(SKILLS_DST) if os.path.isdir(SKILLS_DST) else set()
    copy = sorted(
        f for f in src
        if f not in dst or not filecmp.cmp(os.path.join(SKILLS_SRC, f), os.path.join(SKILLS_DST, f), shallow=False)
    )
    delete = sorted(dst - src)
    return copy, delete


def sync(check_only=False):
    """生成（または差分確認）して、変更点の説明リストを返す。"""
    changes = []

    agents = build_agents_md()
    current = _read(AGENTS_MD) if os.path.exists(AGENTS_MD) else None
    if agents != current:
        changes.append("AGENTS.md")
        if not check_only:
            with open(AGENTS_MD, "w", encoding="utf-8", newline="\n") as f:
                f.write(agents)

    copy, delete = plan_skills()
    changes += [f".agents/skills/{f} (更新)" for f in copy]
    changes += [f".agents/skills/{f} (削除)" for f in delete]
    if not check_only:
        for f in copy:
            dst = os.path.join(SKILLS_DST, f)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copyfile(os.path.join(SKILLS_SRC, f), dst)
        for f in delete:
            os.remove(os.path.join(SKILLS_DST, f))
        # 空になったスキルフォルダを片付ける
        for d, dirs, files in os.walk(SKILLS_DST, topdown=False):
            if d != SKILLS_DST and not os.listdir(d):
                os.rmdir(d)

    size = len(agents.encode("utf-8"))
    limit = _size_limit()
    warn = None
    if size > limit * 0.9:
        warn = (
            f"AGENTS.md が {size:,} バイトで、Codex の読み込み上限（{limit:,} バイト）の9割を超えています。"
            "超えると末尾のルールが読まれません。ルールの圧縮か、.codex/config.toml の project_doc_max_bytes の引き上げを検討してください。"
        )
    return changes, size, warn


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    check_only = "--check" in sys.argv
    changes, size, warn = sync(check_only)
    if check_only:
        if changes:
            print("Codex 用ファイルが古くなっています。python tools/sync-codex.py を実行してください:")
            print("\n".join("  - " + c for c in changes))
        else:
            print(f"Codex 用ファイルは最新です（AGENTS.md {size:,} バイト）。")
    else:
        print(f"同期しました（変更 {len(changes)} 件、AGENTS.md {size:,} バイト）。")
        for c in changes:
            print("  - " + c)
    if warn:
        print("[警告] " + warn)
    if check_only and changes:
        sys.exit(1)


if __name__ == "__main__":
    main()
