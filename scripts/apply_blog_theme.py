#!/usr/bin/env python3
"""Pasang tema blog baru ke semua artikel (blog/) dan draft (drafts/).

Aman dijalankan berulang kali: file yang sudah dipasangi tidak diubah lagi.
Yang dilakukan per file:
  1. Menyisipkan font Manrope + link ke /blog/blog.css sebelum </head>
  2. Menyisipkan top bar (logo NT + tombol Konsultasi) tepat setelah <body>
blog/index.html dilewati karena sudah punya gaya sendiri.
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent

HEAD_ADD = (
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@500;600;700;800&display=swap" rel="stylesheet">\n'
    '<link rel="stylesheet" href="/blog/blog.css">\n'
)

TOPBAR = (
    '<div class="topbar"><div class="tb-inner">'
    '<a class="tb-brand" href="/" aria-label="NAFA Tech — beranda">'
    '<span class="tb-logo">NT</span>'
    '<span class="tb-text"><b>NAFA Tech</b><small>Digital Solution</small></span></a>'
    '<a class="tb-wa" href="https://wa.me/6285290078889" target="_blank" rel="noopener">Konsultasi</a>'
    '</div></div>\n'
)


def targets():
    for folder in ("blog", "drafts"):
        d = ROOT / folder
        if not d.is_dir():
            continue
        for p in sorted(d.glob("*.html")):
            if folder == "blog" and p.name == "index.html":
                continue
            yield p


def patch(text):
    changed = False
    if "/blog/blog.css" not in text and "</head>" in text:
        text = text.replace("</head>", HEAD_ADD + "</head>", 1)
        changed = True
    if 'class="topbar"' not in text:
        m = re.search(r"<body[^>]*>", text)
        if m:
            text = text[: m.end()] + "\n" + TOPBAR + text[m.end():]
            changed = True
    return text, changed


def main():
    n = 0
    for p in targets():
        old = p.read_text(encoding="utf-8")
        new, changed = patch(old)
        if changed:
            p.write_text(new, encoding="utf-8")
            n += 1
            print("dipasang:", p.relative_to(ROOT))
    print(f"Selesai. {n} file diperbarui.")


if __name__ == "__main__":
    main()
