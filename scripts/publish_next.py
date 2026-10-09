import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

WIB = timezone(timedelta(hours=7))
HARI = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
BULAN = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli",
         "Agustus", "September", "Oktober", "November", "Desember"]

now = datetime.now(WIB)
iso = now.strftime("%Y-%m-%d")
tgl = f"{HARI[now.weekday()]}, {now.day} {BULAN[now.month - 1]} {now.year}"

drafts = sorted(Path("drafts").glob("*.html"))
if not drafts:
    print("Tidak ada draft tersisa.")
    sys.exit(0)

src = drafts[0]
slug = re.sub(r"^\d+[-_]", "", src.name)  # buang awalan nomor urut
dest = Path("blog") / slug
if dest.exists():
    print(f"GAGAL: {dest} sudah ada.")
    sys.exit(1)

html = src.read_text(encoding="utf-8")

title = re.search(r"<h1>(.*?)</h1>", html, re.S).group(1).strip()
desc = re.search(r'<meta name="description" content="(.*?)">', html).group(1)
tag = re.search(r'<span class="post-tag">(.*?)</span>', html).group(1)
read = re.search(r"⏱ (.*?)</span>", html).group(1)

# Samakan tanggal di dalam artikel dengan tanggal terbit sebenarnya
html = re.sub(r'"datePublished": "[^"]*"', f'"datePublished": "{iso}"', html)
html = re.sub(r"📅 [^<]*</span>", f"📅 {tgl}</span>", html, count=1)

# 1) Pindahkan artikel ke blog/
dest.write_text(html, encoding="utf-8")
src.unlink()

# 2) Tambah kartu di blog/index.html (paling atas)
card = f'''  <a class="post-card" href="{slug}">
    <span class="post-tag">{tag}</span>
    <div class="post-title">{title}</div>
    <p class="post-excerpt">{desc}</p>
    <div class="post-meta"><span>📅 {tgl}</span><span>⏱ {read}</span></div>
  </a>
'''
idx_path = Path("blog/index.html")
idx = idx_path.read_text(encoding="utf-8")
marker = '<main class="container list">\n'
idx = idx.replace(marker, marker + "\n" + card, 1)
idx_path.write_text(idx, encoding="utf-8")

# 3) Perbarui sitemap.xml
entry = f'''  <url>
    <loc>https://nafatech.web.id/blog/{slug}</loc>
    <lastmod>{iso}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>
'''
sm_path = Path("sitemap.xml")
sm = sm_path.read_text(encoding="utf-8")
sm = re.sub(r"(<loc>https://nafatech\.web\.id/blog/</loc>\s*<lastmod>)[^<]*",
            rf"\g<1>{iso}", sm, count=1)
sm = re.sub(r"(<loc>https://nafatech\.web\.id/blog/</loc>.*?</url>\n)",
            lambda m: m.group(1) + "\n" + entry, sm, count=1, flags=re.S)
sm_path.write_text(sm, encoding="utf-8")

print(f"Terbit: {slug} ({tgl})")
