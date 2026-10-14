# Keputusan Arsitektur (ADR)

Satu file = satu keputusan. Format penamaan: `ADR-NNNN-judul-singkat.md` (empat digit, berurutan tanpa lompat).

## Cara menambah ADR

1. Ambil nomor berikutnya (cek berkas terakhir di folder ini).
2. Salin struktur `ADR-0001-fondasi-teknis.md`: judul, `Status: Diterima | Tanggal: YYYY-MM-DD`, Konteks, Keputusan, Konsekuensi.
3. Satu ADR memuat tepat satu keputusan; keputusan lain = file lain.
4. ADR bersifat **immutable**: jangan edit ADR lama. Bila keputusan berubah, tulis ADR baru berstatus "Diterima" dan sebut "Menggantikan ADR-NNNN" di Konteks; ADR lama cukup diberi catatan satu baris "Digantikan oleh ADR-NNNN" di kepalanya.
5. Perubahan kontrak API/event wajib punya ADR (bump versi + alasan + masa dual-read 30 hari).
6. Perubahan requirement lebih dulu berupa PR di `Pedaree-TownHall`; ADR hanya mencatat keputusan teknis repo.
