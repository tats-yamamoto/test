"""UserPromptSubmit: 現在日時をコンテキストに入れる（Codex 用）
Claude Code 側は settings.json の echo/date で同じことをしている。
Windows でも動くよう Python で出力する。
"""
from datetime import datetime

from _hookio import emit_context

WEEKDAY = "月火水木金土日"


def main():
    now = datetime.now()
    emit_context("UserPromptSubmit", f"現在: {now:%Y-%m-%d %H:%M} ({WEEKDAY[now.weekday()]})")


if __name__ == "__main__":
    main()
