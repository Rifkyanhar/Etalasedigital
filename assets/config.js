// =========================================================
// ISI BAGIAN INI SESUAI AKUN SUPABASE & EMAILJS ANDA
// File ini dipakai oleh dashboard.html DAN oleh setiap
// landing page yang mengirim order (order-form-example.html, promo/index.html, dll)
// =========================================================

// 1. Ambil dari Supabase Dashboard > Project Settings > API
window.NAFA_CONFIG = {
  SUPABASE_URL: "https://uuejlrebqanlkgguerhk.supabase.co",
  SUPABASE_ANON_KEY: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV1ZWpscmVicWFubGtnZ3VlcmhrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODUxNDI3MTIsImV4cCI6MjEwMDcxODcxMn0.CnlC0xknSICXYv1hxCEcqwsSYP8N6QVXHm_Z_xsKluY",

  // 2. Ambil dari akun EmailJS (emailjs.com) — untuk kirim notifikasi
  //    email ke Nafatechid@gmail.com setiap ada order baru.
  EMAILJS_PUBLIC_KEY: "e2TnSlO9POqirXHX3",
  EMAILJS_SERVICE_ID: "service_wussidj",
  EMAILJS_TEMPLATE_ID: "template_cfocasr",
  NOTIF_EMAIL: "Nafatechid@gmail.com",

  // =========================================================
  // 3. SAKLAR UTAMA MIDTRANS
  // =========================================================
  // false = form order manual (pesan.html) yang dipakai SEKARANG,
  //         sambil menunggu approval merchant Midtrans.
  // true  = tombol "Ambil Promo Ini" / "Beli Sekarang" di semua
  //         landing page langsung buka checkout Midtrans Snap
  //         (dengan login Google/Facebook dulu), pesan.html TIDAK
  //         lagi dipakai untuk order baru — otomatis tidak
  //         dirujuk oleh tombol manapun begitu flag ini diganti.
  //
  // Cukup ubah SATU baris ini jadi true, lalu push ke repo —
  // TIDAK perlu edit ulang index.html, promo/index.html, atau
  // halaman lain manapun, karena semuanya baca nilai dari sini.
  MIDTRANS_ACTIVE: false,

  // 4. Client Key dari dashboard Midtrans (bukan Server Key!).
  //    Dipakai untuk load Snap.js. Isi setelah akun Midtrans aktif.
  MIDTRANS_CLIENT_KEY: "ISI_SETELAH_MIDTRANS_ACC",
  // Ganti ke false setelah live/production (bukan sandbox lagi)
  MIDTRANS_IS_SANDBOX: true
};
