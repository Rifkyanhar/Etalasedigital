/*!
 * NAFA Tech — Google Analytics 4 (satu file untuk seluruh halaman)
 * Pasang SATU baris ini sebelum </head>:
 *   <script src="https://nafatech.web.id/assets/ga4.js" defer></script>
 *
 * - Bila halaman sudah memuat tag GA4 sendiri (mis. index.html), pemuatan dasar dilewati
 *   supaya kunjungan tidak terhitung ganda; pelacakan klik di bawah tetap jalan.
 * - Klik tombol dikirim sebagai peristiwa GA4 yang sejajar dengan Meta Pixel:
 *     klik WhatsApp         -> generate_lead (method: whatsapp)
 *     klik Order / Langganan -> begin_checkout
 *     klik Coba Demo        -> demo_click
 * - Tandai generate_lead sebagai "peristiwa utama" (key event) di GA4 agar terhitung sebagai konversi.
 */
(function () {
  "use strict";
  var GA_ID = "G-3LYLYZX1PE";

  // Fungsi aman dipanggil dari mana pun
  window.nafaGA = window.nafaGA || function () {};

  if (!/(^|\.)nafatech\.web\.id$/.test(location.hostname)) return;   // abaikan localhost / pratinjau
  if (window.__nafaGA4) return;
  window.__nafaGA4 = true;

  var alreadyHasTag = !!document.querySelector('script[src*="googletagmanager.com/gtag/js?id=' + GA_ID + '"]');
  if (!alreadyHasTag) {
    window.dataLayer = window.dataLayer || [];
    window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
    var s = document.createElement("script");
    s.async = true;
    s.src = "https://www.googletagmanager.com/gtag/js?id=" + GA_ID;
    document.head.appendChild(s);
    window.gtag("js", new Date());
    window.gtag("config", GA_ID);
  }

  function send(name, params) {
    if (typeof window.gtag === "function") { try { window.gtag("event", name, params || {}); } catch (e) {} }
  }
  window.nafaGA = send;

  function qs(href, key) {
    try { return new URL(href, location.href).searchParams.get(key) || ""; } catch (e) { return ""; }
  }

  document.addEventListener("click", function (ev) {
    var a = ev.target && ev.target.closest ? ev.target.closest("a[href]") : null;
    if (!a) return;
    var href = a.getAttribute("href") || "";
    var label = (a.textContent || "").replace(/\s+/g, " ").trim().slice(0, 80);

    if (/wa\.me\//.test(href)) {
      send("generate_lead", { method: "whatsapp", link_text: label, page_title: document.title });
    } else if (/pesan\.html|langganan\.html/.test(href)) {
      var item = qs(href, "layanan") || qs(href, "product") || qs(href, "service_id") || label;
      send("begin_checkout", {
        items: [{ item_name: item }],
        mode: /langganan\.html/.test(href) ? "langganan" : "sekali_bayar"
      });
    } else if (/demo/i.test(label) && !/^#/.test(href)) {
      send("demo_click", { link_text: label, page_title: document.title });
    }
  }, true);
})();
