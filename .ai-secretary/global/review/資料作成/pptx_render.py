# -*- coding: utf-8 -*-
"""
pptx → PNG 書き出し（PowerPoint COM）。目視チェック用。
使い方: python pptx_render.py <file.pptx> [out_dir] [slide_no]
  slide_no を指定するとその1枚だけ書き出す。
出力: <file>_png/Slide{N}.PNG（PowerPoint既定の連番）
"""
import sys, os
import win32com.client


def render(path, outdir=None, width=1920, slide_no=None):
    path = os.path.abspath(path)
    if outdir is None:
        outdir = os.path.splitext(path)[0] + "_png"
    os.makedirs(outdir, exist_ok=True)
    height = int(round(width * 7.5 / 13.333))
    app = win32com.client.Dispatch("PowerPoint.Application")
    app.Visible = True  # COM は非表示だと Open/Export で落ちることがある
    try:
        pres = app.Presentations.Open(path, ReadOnly=True, WithWindow=False)
        if slide_no:
            out = os.path.join(outdir, f"Slide{slide_no}.PNG")
            pres.Slides(slide_no).Export(out, "PNG", width, height)
        else:
            pres.Export(outdir, "PNG", width, height)
        pres.Close()
    finally:
        app.Quit()
    print("rendered ->", outdir)
    return outdir


if __name__ == "__main__":
    p = sys.argv[1]
    od = sys.argv[2] if len(sys.argv) > 2 else None
    sn = int(sys.argv[3]) if len(sys.argv) > 3 else None
    render(p, od, slide_no=sn)
