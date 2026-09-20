// =========================================================
// GANTI 2 NILAI DI BAWAH INI dengan milik project Supabase kamu
// Ambil di: Supabase Dashboard > Project Settings > API
// =========================================================
const SUPABASE_URL = "https://xxxxxxxxxxxx.supabase.co";
const SUPABASE_ANON_KEY = "isi-anon-public-key-disini";

// Inisialisasi client Supabase (dipakai di semua halaman)
const supabaseClient = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
