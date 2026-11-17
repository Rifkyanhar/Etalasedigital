import html as htmllib
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

SITE = "https://nafatech.web.id"
LOGO = f"{SITE}/image/logo-nafatech.jpeg"
FONT_HREF = ("https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700"
             "&family=Inter:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap")

WIB = timezone(timedelta(hours=7))
HARI = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
BULAN = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli",
         "Agustus", "September", "Oktober", "November", "Desember"]

now = datetime.now(WIB)
iso = now.strftime("%Y-%m-%d")
tgl = f"{HARI[now.weekday()]}, {now.day} {BULAN[now.month - 1]} {now.year}"


def must(pattern, text, label, filename, flags=0):
    m = re.search(pattern, text, flags)
    if not m:
        raise SystemExit(f"GAGAL: bagian '{label}' tidak ditemukan di draft {filename}")
    return m.group(1)


def enhance(html, slug, title, desc):
    """Rapikan bagian <head> artikel supaya semua artikel punya SEO dasar yang sama."""
    url = f"{SITE}/blog/{slug}"

    # 1) canonical selalu cocok dengan alamat terbit
    html = re.sub(r'<link rel="canonical" href="[^"]*">',
                  f'<link rel="canonical" href="{url}">', html, count=1)

    # 2) <title>: buang akhiran merek kalau kepanjangan (batas aman 60 karakter)
    def fix_title(m):
        t = m.group(1).strip()
        if len(t) > 60 and t.endswith(" | NAFA Tech"):
            t = t[: -len(" | NAFA Tech")]
        if len(t) > 60:
            print(f"PERINGATAN: <title> {len(t)} karakter (>60), pendekkan manual di draft: {t}")
        return f"<title>{t}</title>"
    html = re.sub(r"<title>(.*?)</title>", fix_title, html, count=1, flags=re.S)

    # 3) tambah meta Open Graph / Twitter yang belum ada
    wanted = [
        ("og:site_name", '<meta property="og:site_name" content="NAFA Tech">'),
        ("og:locale", '<meta property="og:locale" content="id_ID">'),
        ("og:url", f'<meta property="og:url" content="{url}">'),
        ("og:image", f'<meta property="og:image" content="{LOGO}">'),
        ("twitter:card", '<meta name="twitter:card" content="summary_large_image">'),
        ("twitter:title", f'<meta name="twitter:title" content="{title}">'),
        ("twitter:description", f'<meta name="twitter:description" content="{desc}">'),
        ("twitter:image", f'<meta name="twitter:image" content="{LOGO}">'),
    ]
    missing = [tag for key, tag in wanted if f'"{key}"' not in html]
    if missing:
        html = re.sub(r'(<link rel="canonical"[^>]*>)',
                      lambda m: m.group(1) + "\n" + "\n".join(missing), html, count=1)

    # 4) satukan permintaan Google Fonts yang dobel
    if "<style>" in html and len(re.findall(r'<link[^>]*fonts\.googleapis\.com/css2[^>]*>', html)) > 1:
        html = re.sub(r'<link rel="preconnect"[^>]*>\s*', "", html)
        html = re.sub(r'<link[^>]*fonts\.googleapis\.com/css2[^>]*>\s*', "", html)
        fonts = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
                 '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
                 f'<link href="{FONT_HREF}" rel="stylesheet">\n')
        html = html.replace("<style>", fonts + "<style>", 1)

    # 5) data terstruktur: lengkapi Article, tambah BreadcrumbList kalau belum ada
    state = {"breadcrumb": False}

    def fix_ld(m):
        try:
            data = json.loads(m.group(1))
        except ValueError:
            return m.group(0)
        if not isinstance(data, dict):
            return m.group(0)
        if data.get("@type") == "BreadcrumbList":
            state["breadcrumb"] = True
            return m.group(0)
        if data.get("@type") != "Article":
            return m.group(0)
        data["datePublished"] = iso
        data["dateModified"] = iso
        data.setdefault("image", LOGO)
        data.setdefault("inLanguage", "id")
        data["mainEntityOfPage"] = {"@type": "WebPage", "@id": url}
        if not isinstance(data.get("author"), dict):
            data["author"] = {"@type": "Organization", "name": "NAFA Tech"}
        data["author"].setdefault("url", SITE + "/")
        if not isinstance(data.get("publisher"), dict):
            data["publisher"] = {"@type": "Organization", "name": "NAFA Tech"}
        data["publisher"].setdefault("logo", {"@type": "ImageObject", "url": LOGO})
        return ('<script type="application/ld+json">\n'
                + json.dumps(data, ensure_ascii=False, indent=2) + "\n</script>")

    html = re.sub(r'<script type="application/ld\+json">\s*(.*?)\s*</script>',
                  fix_ld, html, flags=re.S)

    if not state["breadcrumb"]:
        plain = htmllib.unescape(re.sub(r"<[^>]+>", "", title))
        crumb = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Beranda", "item": SITE + "/"},
                {"@type": "ListItem", "position": 2, "name": "Artikel", "item": SITE + "/blog/"},
                {"@type": "ListItem", "position": 3, "name": plain},
            ],
        }
        block = ('<script type="application/ld+json">\n'
                 + json.dumps(crumb, ensure_ascii=False, indent=2) + "\n</script>\n")
        html = html.replace("</head>", block + "</head>", 1)

    return html


def publish(src, slug, dest):
    html = src.read_text(encoding="utf-8")
    name = src.name

    title = must(r"<h1>(.*?)</h1>", html, "judul <h1>", name, re.S).strip()
    desc = must(r'<meta name="description" content="(.*?)">', html, "meta description", name)
    tag = must(r'<span class="post-tag">(.*?)</span>', html, "post-tag", name)
    read = must(r"⏱ (.*?)</span>", html, "waktu baca (⏱)", name)

    # tanggal di dalam artikel = tanggal terbit sebenarnya
    html = re.sub(r"📅 [^<]*</span>", f"📅 {tgl}</span>", html, count=1)
    html = re.sub(r'"datePublished": "[^"]*"', f'"datePublished": "{iso}"', html)
    html = enhance(html, slug, title, desc)

    # 1) pindahkan artikel ke blog/
    dest.write_text(html, encoding="utf-8")
    src.unlink()

    # 2) tambah kartu di blog/index.html (paling atas)
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
    if marker not in idx:
        print("PERINGATAN: penanda <main class=\"container list\"> tidak ada di blog/index.html, kartu tidak ditambahkan")
    else:
        idx = idx.replace(marker, marker + "\n" + card, 1)
        idx_path.write_text(idx, encoding="utf-8")

    # 3) tambah artikel ke sitemap.xml
    entry = f'''  <url>
    <loc>{SITE}/blog/{slug}</loc>
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


def maintain_sitemap():
    """Buang alamat yang filenya tidak ada (penyebab 404 di sitemap) dan tambah halaman jasa-*.html yang belum terdaftar."""
    sm_path = Path("sitemap.xml")
    if not sm_path.exists():
        return
    sm = original = sm_path.read_text(encoding="utf-8")
    present = set()
    for block in re.findall(r"<url>.*?</url>", sm, re.S):
        loc = re.search(r"<loc>(.*?)</loc>", block).group(1).strip()
        if not loc.startswith(SITE + "/"):
            present.add(loc)
            continue
        rel = loc[len(SITE) + 1:]
        if rel == "":
            f = Path("index.html")
        elif rel.endswith("/"):
            f = Path(rel) / "index.html"
        else:
            f = Path(rel)
        if f.exists():
            present.add(loc)
        else:
            print(f"Sitemap: membuang {loc} (file {f} tidak ada)")
            sm = sm.replace(block, "", 1)

    adds = ""
    for f in sorted(Path(".").glob("jasa-*.html")):
        loc = f"{SITE}/{f.name}"
        if loc not in present:
            print(f"Sitemap: menambah {loc}")
            adds += f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{iso}</lastmod>\n  </url>\n"
    if adds:
        sm = sm.replace("</urlset>", adds + "</urlset>")

    sm = re.sub(r"[ \t]+\n", "\n", sm)
    sm = re.sub(r"\n{3,}", "\n\n", sm)
    if sm != original:
        sm_path.write_text(sm, encoding="utf-8")


def check_links():
    """Laporkan tautan internal ke halaman .html yang tidak ada (hanya peringatan di log)."""
    pages = list(Path("blog").glob("*.html"))
    if Path("index.html").exists():
        pages.append(Path("index.html"))
    found = 0
    for p in pages:
        html = p.read_text(encoding="utf-8", errors="ignore")
        for href in sorted(set(re.findall(r'href="([^"]+)"', html))):
            if re.match(r"(https?:|mailto:|tel:|#|javascript:|//)", href):
                continue
            path = re.split(r"[#?]", href)[0]
            if not (path.endswith(".html") or path.endswith("/")):
                continue
            target = Path(path.lstrip("/")) if path.startswith("/") else p.parent / path
            if path.endswith("/"):
                target = target / "index.html"
            if not target.exists():
                found += 1
                print(f"PERINGATAN LINK RUSAK: {p} -> {href}")
    if found == 0:
        print("Cek link internal: tidak ada yang rusak.")


def main():
    drafts = sorted(Path("drafts").glob("*.html"))
    published = False
    if not drafts:
        print("Tidak ada draft tersisa.")
    for src in drafts:
        slug = re.sub(r"^\d+[-_]", "", src.name)  # buang awalan nomor urut
        dest = Path("blog") / slug
        if dest.exists():
            print(f"PERINGATAN: {dest} sudah ada, draft {src.name} dilewati (hapus draft ini bila sudah tidak dipakai).")
            continue
        publish(src, slug, dest)
        published = True
        break

    maintain_sitemap()
    check_links()

    if drafts and not published:
        print("GAGAL: tidak ada draft yang bisa diterbitkan.")
        sys.exit(1)


main()
