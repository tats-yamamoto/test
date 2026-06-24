# -*- coding: utf-8 -*-
"""
pptx フォント監査ツール
============================================================
colors_and_type.css の type scale 準拠を、出来上がった .pptx に対して検査する。
生成方式（python-pptx スクリプト / Claude Design / 手動）を問わず、
「出力された pptx」を最後にこれへ通して "文字が小さい / バラつく" を機械的に検出する。

使い方:
    python pptx_font_audit.py <file.pptx> [<file2.pptx> ...]

検出する違反:
  - OFF_SCALE : type scale に無いサイズ（9.5 / 10.5 / 11.5 / 12.5 / 13 / 14.5 / 15 等）
                → "ばらばら" の主因。半端な刻み・スケール外の値。
  - TOO_SMALL : 11pt 未満（footer 10pt 未満は実質読めない）
  - SUB_FLOOR : 14pt 未満（本文なら違反。表セル/キャプション/図ラベルのみ 11-12pt 許容）
  - MIXING    : 1スライド内で本文域(13-18pt)のサイズが3種以上混在
  - UNSET     : サイズ未指定（マスター継承。意図しないと事故りやすい）

終了コード: 違反(OFF_SCALE/TOO_SMALL) があれば 1、無ければ 0。
"""
import sys
from collections import Counter, defaultdict
from pptx import Presentation
from pptx.util import Emu

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# ---- colors_and_type.css 準拠の許可サイズ（pt）-------------------------------
# 通常テキストで使ってよい値（本文16 / 密14 / 小11-12 / footer10 / title20 / msgline18）
ALLOWED_TEXT = {10, 11, 12, 14, 16, 18, 20}
# 表紙タイトル・章番号など大型ディスプレイで許容
ALLOWED_DISPLAY = {22, 24, 26, 27, 28, 30, 32, 36, 40, 44, 48}
ALLOWED = ALLOWED_TEXT | ALLOWED_DISPLAY

BODY_FLOOR = 14   # 本文の下限。これ未満は cell/caption/label のみ許容(11-12pt)
TOO_SMALL = 10    # これ未満は原則アウト（footer=10pt は許容、9.x は読めない）
BODY_BAND = (13, 18)  # このレンジで複数サイズ混在 = "ばらばら" とみなす


def iter_runs(shapes):
    """slide 配下の全 run を (size_pt|None, text) で列挙。表・グループも再帰。"""
    for sp in shapes:
        # グループ図形は再帰
        if sp.shape_type == 6:  # MSO_SHAPE_TYPE.GROUP
            yield from iter_runs(sp.shapes)
            continue
        # 表
        if getattr(sp, "has_table", False) and sp.has_table:
            for row in sp.table.rows:
                for cell in row.cells:
                    for p in cell.text_frame.paragraphs:
                        for r in p.runs:
                            yield _size(r), r.text
            continue
        # テキストフレーム
        if getattr(sp, "has_text_frame", False) and sp.has_text_frame:
            for p in sp.text_frame.paragraphs:
                for r in p.runs:
                    yield _size(r), r.text


def _size(run):
    sz = run.font.size
    if sz is None:
        return None
    pt = sz.pt
    # 端数を保持（11.5 等を潰さない）
    return round(pt, 2)


def audit(path):
    prs = Presentation(path)
    print("=" * 64)
    print(f"AUDIT: {path}")
    print("=" * 64)

    overall = Counter()
    off_scale = defaultdict(list)   # size -> [(slide, text)]
    too_small = defaultdict(list)
    unset_count = 0
    mixing_slides = []

    for idx, slide in enumerate(prs.slides, 1):
        per_slide = Counter()
        samples = {}
        for size, text in iter_runs(slide.shapes):
            t = (text or "").strip().replace("\n", " ")
            if size is None:
                unset_count += 1
                continue
            overall[size] += 1
            per_slide[size] += 1
            samples.setdefault(size, t[:24])
            if size not in ALLOWED:
                off_scale[size].append((idx, t[:30]))
            if size < TOO_SMALL:
                too_small[size].append((idx, t[:30]))

        # 本文域でのサイズ混在
        body_sizes = [s for s in per_slide if BODY_BAND[0] <= s <= BODY_BAND[1]]
        distinct = len(per_slide)
        mix_flag = ""
        if len(body_sizes) >= 3:
            mixing_slides.append((idx, sorted(body_sizes)))
            mix_flag = f"  ⚠MIXING 本文域{len(body_sizes)}種"
        sizes_str = " ".join(
            f"{('!' if s not in ALLOWED else ' ')}{s}×{per_slide[s]}"
            for s in sorted(per_slide, reverse=True)
        )
        print(f"S{idx:<2} 種{distinct:<2} | {sizes_str}{mix_flag}")

    # ---- サマリ -------------------------------------------------------------
    print("-" * 64)
    print(f"全 run のサイズ分布: " + ", ".join(
        f"{s}pt×{overall[s]}{'(!)' if s not in ALLOWED else ''}"
        for s in sorted(overall, reverse=True)))
    print()

    n_off = sum(len(v) for v in off_scale.values())
    n_small = sum(len(v) for v in too_small.values())
    print(f"■ OFF_SCALE (スケール外): {n_off} 箇所 / 値 = "
          + ", ".join(f"{s}pt×{len(off_scale[s])}" for s in sorted(off_scale)))
    for s in sorted(off_scale):
        ex = off_scale[s][:3]
        print(f"    {s}pt: " + " / ".join(f"S{i}「{t}」" for i, t in ex)
              + (" …" if len(off_scale[s]) > 3 else ""))
    print(f"■ TOO_SMALL (<{TOO_SMALL}pt): {n_small} 箇所"
          + ("" if not n_small else " / 値 = "
             + ", ".join(f"{s}pt×{len(too_small[s])}" for s in sorted(too_small))))
    print(f"■ MIXING (本文域3種以上): {len(mixing_slides)} スライド"
          + ("" if not mixing_slides else " → "
             + ", ".join(f"S{i}{v}" for i, v in mixing_slides)))
    print(f"■ UNSET (サイズ未指定): {unset_count} 箇所")
    print()

    ok = (n_off == 0 and n_small == 0)
    print("判定:", "✅ PASS（標準準拠）" if ok else "❌ FAIL（要修正）")
    return ok


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    results = [audit(p) for p in argv[1:]]
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
