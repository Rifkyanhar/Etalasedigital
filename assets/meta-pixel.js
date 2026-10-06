/*!
 * NAFA Tech — Meta Pixel (Facebook + Instagram)
 * Satu file untuk seluruh situs nafatech.web.id. Instagram TIDAK punya pixel
 * terpisah: satu Meta Pixel dipakai untuk iklan Facebook dan Instagram.
 *
 * CARA PAKAI
 * 1. Buat Pixel di Meta Events Manager, salin ID-nya (angka), tempel di PIXEL_ID di bawah.
 * 2. Pasang SATU baris ini sebelum </head> di setiap halaman:
 *      <script src="https://nafatech.web.id/assets/meta-pixel.js" defer></script>
 * 3. Selama PIXEL_ID masih berisi teks "GANTI_...", skrip ini tidak melakukan apa pun.
 *
 * YANG DILACAK OTOMATIS (layanan baru ikut terlacak tanpa edit tambahan)
 *   PageView           setiap halaman dibuka
 *   ViewContent        panel detail layanan dibuka (nama layanan dibaca dari panelnya)
 *   Contact            klik tombol WhatsApp (wa.me)
 *   InitiateCheckout   klik tombol Order / Langganan (pesan.html, langganan.html)
 *   DemoClick (custom) klik tombol Coba Demo
 *   Purchase           dipanggil manual dari kode saat pembayaran sukses:
 *                      nafaTrack('Purchase', { value: 750000, currency: 'IDR', content_name: '...' })
 */
(function () {
  "use strict";

  var PIXEL_ID = "GANTI_DENGAN_PIXEL_ID";

  // Fungsi kosong supaya pemanggilan nafaTrack(...) di halaman mana pun tidak pernah error
  window.nafaTrack = window.nafaTrack || function () {};

  if (!/^\d{8,20}$/.test(PIXEL_ID)) return;                                   // belum diisi
  if (!/(^|\.)nafatech\.web\.id$/.test(location.hostname)) return;            // hanya domain asli
  if (window.__nafaPixelLoaded) return;                                       // cegah pasang ganda
  window.__nafaPixelLoaded = true;

  // --- Kode dasar resmi Meta Pixel ---
  !function (f, b, e, v, n, t, s) {
    if (f.fbq) return;
    n = f.fbq = function () { n.callMethod ? n.callMethod.apply(n, arguments) : n.queue.push(arguments); };
    if (!f._fbq) f._fbq = n;
    n.push = n; n.loaded = !0; n.version = "2.0"; n.queue = [];
    t = b.createElement(e); t.async = !0; t.src = v;
    s = b.getElementsByTagName(e)[0]; s.parentNode.insertBefore(t, s);
  }(window, document, "script", "https://connect.facebook.net/en_US/fbevents.js");

  fbq("init", PIXEL_ID);
  fbq("track", "PageView");

  var sentOnce = {};
  window.nafaTrack = function (name, params, onceKey) {
    if (onceKey) { if (sentOnce[onceKey]) return; sentOnce[onceKey] = true; }
    try { fbq("track", name, params || {}); } catch (e) {}
  };
  function custom(name, params) { try { fbq("trackCustom", name, params || {}); } catch (e) {} }

  function qs(href, key) {
    try { return new URL(href, location.href).searchParams.get(key) || ""; } catch (e) { return ""; }
  }

  // --- Klik tombol: WhatsApp, Order/Langganan, Demo ---
  document.addEventListener("click", function (ev) {
    var a = ev.target && ev.target.closest ? ev.target.closest("a[href]") : null;
    if (!a) return;
    var href = a.getAttribute("href") || "";
    var label = (a.textContent || "").replace(/\s+/g, " ").trim().slice(0, 80);

    if (/wa\.me\//.test(href)) {
      window.nafaTrack("Contact", { content_name: document.title, button: label });
    } else if (/pesan\.html|langganan\.html/.test(href)) {
      var item = qs(href, "layanan") || qs(href, "product") || qs(href, "service_id") || label;
      window.nafaTrack("InitiateCheckout", {
        content_name: item, content_type: "product",
        mode: /langganan\.html/.test(href) ? "langganan" : "sekali_bayar"
      });
    } else if (/demo/i.test(label) && !/^#/.test(href)) {
      custom("DemoClick", { content_name: document.title, button: label });
    }
  }, true);

  // --- ViewContent: panel detail layanan di index.html (berlaku untuk layanan baru juga) ---
  function watchPanel() {
    var overlay = document.getElementById("overlay");
    if (!overlay || !window.MutationObserver) return;
    var wasOpen = false;
    new MutationObserver(function () {
      var open = overlay.classList.contains("show");
      if (open && !wasOpen) {
        var t = document.getElementById("panelTitle");
        var c = document.getElementById("panelCat");
        window.nafaTrack("ViewContent", {
          content_name: t ? t.textContent.trim() : "",
          content_category: c ? c.textContent.trim() : "",
          content_type: "product"
        });
      }
      wasOpen = open;
    }).observe(overlay, { attributes: true, attributeFilter: ["class"] });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", watchPanel);
  else watchPanel();
})();
