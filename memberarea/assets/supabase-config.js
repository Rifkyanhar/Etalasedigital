// =========================================================
// GANTI 2 NILAI DI BAWAH INI dengan milik project Supabase kamu
// Ambil di: Supabase Dashboard > Project Settings > API
// =========================================================
const SUPABASE_URL = "https://uuejlrebqanlkgguerhk.supabase.co";
const SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV1ZWpscmVicWFubGtnZ3VlcmhrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODUxNDI3MTIsImV4cCI6MjEwMDcxODcxMn0.CnlC0xknSICXYv1hxCEcqwsSYP8N6QVXHm_Z_xsKluY";

// Inisialisasi client Supabase (dipakai di semua halaman)
const supabaseClient = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
