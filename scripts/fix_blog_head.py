"""Perbaikan sekali jalan untuk artikel yang SUDAH terbit di blog/.
Hanya menyentuh bagian <head> (title, Open Graph, Twitter card, font, data terstruktur).
Isi artikel dan tanggal terbit tidak diubah. Aman dijalankan berulang.

Tanpa argumen  : hanya laporan (dry run), tidak mengubah file.
Dengan --apply : menulis perubahan ke file.
"""
import html as htmllib
import json
import re
import sys
from pathlib import Path

SITE = "https://nafatech.web.id"
LOGO = f"{SITE}/image/logo-nafatech.jpeg"
FONT_HREF = ("https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700"
             "&family=Inter:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap")
SUFFIXES = [" | NAFA Tech", " — NAFA Tech", " – NAFA Tech", " - NAFA Tech"]
APPLY = "--apply" in sys.argv


def fix(html, slug, name, report):
    url = f"{SITE}/blog/{slug}"
    title_m = re.search(r"<title>(.*?)</title>", html, re.S)
    desc_m = re.search(r'<meta name="description" content="(.*?)">', html)
    if not title_m or not desc_m:
        report["dilewati"].append(f"{name} (tidak ada <title> atau meta description)")
        return html
    desc = desc_m.group(1)
    h1_m = re.search(r"<h1>(.*?)</h1>", html, re.S)
    h1 = h1_m.group(1).strip() if h1_m else title_m.group(1).strip()

    # 1) canonical
    canon = f'<link rel="canonical" href="{url}">'
    if re.search(r'<link rel="canonical" href="[^"]*">', html):
        html = re.sub(r'<link rel="canonical" href="[^"]*">', canon, html, count=1)
    else:
        html = html.replace(desc_m.group(0), desc_m.group(0) + "\n" + canon, 1)

    # 2) title: buang akhiran merek kalau kepanjangan
    def fix_title(m):
        t = m.group(1).strip()
        if len(htmllib.unescape(t)) > 60:
            for s in SUFFIXES:
                if t.endswith(s):
                    t = t[: -len(s)]
                    break
        return f"<title>{t}</title>"
    html = re.sub(r"<title>(.*?)</title>", fix_title, html, count=1, flags=re.S)
    final_title = htmllib.unescape(re.search(r"<title>(.*?)</title>", html, re.S).group(1).strip())
    if len(final_title) > 60:
        report["title_panjang"].append(f"{name}: {len(final_title)} karakter - {final_title}")
    if len(htmllib.unescape(desc)) > 160:
        report["desc_panjang"].append(f"{name}: {len(htmllib.unescape(desc))} karakter")

    # 3) Open Graph + Twitter yang belum ada
    wanted = [
        ("og:type", '<meta property="og:type" content="article">'),
        ("og:site_name", '<meta property="og:site_name" content="NAFA Tech">'),
        ("og:locale", '<meta property="og:locale" content="id_ID">'),
        ("og:title", f'<meta property="og:title" content="{h1}">'),
        ("og:description", f'<meta property="og:description" content="{desc}">'),
        ("og:url", f'<meta property="og:url" content="{url}">'),
        ("og:image", f'<meta property="og:image" content="{LOGO}">'),
        ("twitter:card", '<meta name="twitter:card" content="summary_large_image">'),
        ("twitter:title", f'<meta name="twitter:title" content="{h1}">'),
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

    # 5) data terstruktur (tanggal terbit TIDAK diubah)
    state = {"crumb": False}

    def fix_ld(m):
        try:
            data = json.loads(m.group(1))
        except ValueError:
            return m.group(0)
        if not isinstance(data, dict):
            return m.group(0)
        if data.get("@type") == "BreadcrumbList":
            state["crumb"] = True
            return m.group(0)
        if data.get("@type") != "Article":
            return m.group(0)
        if data.get("datePublished"):
            data.setdefault("dateModified", data["datePublished"])
        data.setdefault("image", LOGO)
        data.setdefault("inLanguage", "id")
        if not isinstance(data.get("mainEntityOfPage"), dict):
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

    if not state["crumb"]:
        plain = htmllib.unescape(re.sub(r"<[^>]+>", "", h1))
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


def main():
    report = {"dilewati": [], "title_panjang": [], "desc_panjang": []}
    files = [p for p in sorted(Path("blog").glob("*.html")) if p.name != "index.html"]
    changed = 0
    for p in files:
        old = p.read_text(encoding="utf-8")
        new = fix(old, p.name, p.name, report)
        if new != old:
            changed += 1
            if APPLY:
                p.write_text(new, encoding="utf-8")

    mode = "DITERAPKAN" if APPLY else "DRY RUN (belum ada file yang diubah)"
    print(f"Mode: {mode}")
    print(f"Artikel diperiksa: {len(files)} | akan/telah diubah: {changed}")
    for title, key in [("Dilewati", "dilewati"),
                       ("Title masih lebih dari 60 karakter (pendekkan manual)", "title_panjang"),
                       ("Meta description lebih dari 160 karakter (pendekkan manual)", "desc_panjang")]:
        print(f"\n{title}: {len(report[key])}")
        for line in report[key]:
            print("  - " + line)


main()
