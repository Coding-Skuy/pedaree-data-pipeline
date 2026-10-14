# AGENTS.md — pedaree-data-pipeline

Repo `pedaree-data-pipeline` adalah pipa data Pedaree yang meneruskan event stok sebagai sinyal anjuran restock ke TitipO (kontrak bilateral `pedaree.stok.v1`) dan menghitung agregat stockout/waste.

## Sumber kebenaran

Seluruh requirement berada di `Pedaree-TownHall` (versi beku v1.0.0). Repo ini dilarang menduplikasi requirement; bila requirement berubah, buka PR di TownHall dulu.

| Dokumen | Isi yang mengikat repo ini |
|---|---|
| [`platform/versions/v1.0.0/BRD/30-demand-metrik.md`](https://github.com/Coding-Skuy/Pedaree-TownHall/blob/main/platform/versions/v1.0.0/BRD/30-demand-metrik.md) | BR-301..BR-306: debounce sinyal, waste, target bulan ke-3, event analitik, `pedaree.stok.v1`, tampilan |
| [`inventori/10-model-stok-dapur.md`](https://github.com/Coding-Skuy/Pedaree-TownHall/blob/main/inventori/10-model-stok-dapur.md) | Model stok: PantryItem, StokBatch, MutasiStok, aturan hitung FEFO, batas 400 item / 2.000 batch |
| [`inventori/20-satuan-hortikultura.md`](https://github.com/Coding-Skuy/Pedaree-TownHall/blob/main/inventori/20-satuan-hortikultura.md) | SUMBER SAH 13 satuan baku, konversi, pembulatan, bobot acuan, validasi input |
| [`metrik/10-stockout-dan-waste.md`](https://github.com/Coding-Skuy/Pedaree-TownHall/blob/main/metrik/10-stockout-dan-waste.md) | Definisi dan rumus stockout/waste, target bulan ke-3, event analitik, tampilan |
| [`platform/versions/v1.0.0/SRS/30-non-functional.md`](https://github.com/Coding-Skuy/Pedaree-TownHall/blob/main/platform/versions/v1.0.0/SRS/30-non-functional.md) | Kebutuhan non-fungsional |
| [`platform/versions/v1.0.0/SRS/40-acceptance-criteria.md`](https://github.com/Coding-Skuy/Pedaree-TownHall/blob/main/platform/versions/v1.0.0/SRS/40-acceptance-criteria.md) | QA-001..QA-003 (semua acceptance menjadi test, build merah gagal, regresi wajib test) |
| [`KONTEKS-LINTAS-DIVISI.md`](https://github.com/Coding-Skuy/ChefGenie-TownHall/blob/main/KONTEKS-LINTAS-DIVISI.md) (ChefGenie-TownHall) | Kontrak bilateral `pedaree.stok.v1` (§3.1), satuan/ID/uang (§6), metrik (§7), isu terbuka (§8) |
| [`townhall-roadmap.md`](https://github.com/Coding-Skuy/ChefGenie-TownHall/blob/main/townhall-roadmap.md) | Batas context (§2) dan Definisi selesai (§6) |

Dokumen turunan repo ini: `versions/v1.0.0/docs/40-TECHSTACK.md` dan `versions/v1.0.0/docs/60-BLAST-RADIUS.md` (beku, tidak diedit), pelengkapnya `docs/ARSITEKTUR-AI-DEV.md` (matriks stack rinci + batas context), dan keputusan di `docs/decisions/`.

## Tech stack terkunci

- **Python** (kondisi saat ini 3.12.8): pydantic 2.10.6, httpx 0.28.1, psycopg[binary] 3.2.4, pytest 8.3.4, ruff 0.8.9.
- Kontrak event berversi + amplop idempoten (KONTEKS §3): kunci idempoten konsumen `item_id + tanggal`; retry 3× (5/30/300 dtk) lalu DLQ; konsumen tercatat = TitipO.
- Keluaran: `POST /sinyal/pedaree-stok` ke TitipO dengan header `X-Service-Key` (201 `dicatat_sebagai_anjuran`, 200 `duplikat_diabaikan`).
- Dedup produsen: maks 1 sinyal per item per 24 jam (BR-301); relevansi anjuran 48 jam; TIDAK PERNAH membuat pesanan otomatis.
- Agregat metrik: stockoutRate harian pukul 23:59 WIB, wasteGram/wasteRupiah bulanan WIB, median jam MENIPIS ke HABIS (`metrik/10`).

Larangan: menulis ke DB divisi lain; menambah jenis sinyal di luar 3 jenis terkunci tanpa bump versi + 30 hari dual-read; mengubah payload tanpa memberi tahu TitipO; membuat pesanan otomatis.

## Invarian domain Pedaree (terkunci v1.0.0)

- **FEFO**: `PAKAI` selalu memotong batch dengan `tanggalKedaluwarsa` paling dekat lebih dulu; bila tanggal `null` (garam, gula) batch tertua keluar dulu (FIFO). Batch `KEDALUWARSA` terkunci dari FEFO dan hanya bisa dibuang. Stok selalu berbentuk batch; setiap perubahan `jumlahAktif` menulis satu `MutasiStok` (tidak ada perubahan stok tanpa mutasi).
- **13 satuan baku** — sumber sah `inventori/20-satuan-hortikultura.md` (BUKAN BRD `10-inventori.md` BR-103 maupun BRD `20-satuan-hortikultura.md`; KONTEKS §8.5): `gram`, `kg`, `ml`, `liter`, `sdm`, `sdt`, `pcs`, `siung`, `buah`, `ikat`, `batang`, `bonggol`, `lembar`. `kg` disimpan sebagai gram (×1000); `liter`/`sdm`/`sdt` disimpan sebagai ml (×1000 / ×15 / ×5). Satuan hitung pecahan ditolak; jumlah >50.000 g atau >50.000 ml per batch ditolak (pecah jadi beberapa batch); komoditas di luar tabel bobot hanya boleh gram, kg, ml, liter, sdm, sdt, pcs.
- **Target keberhasilan** (townhall-roadmap §2; `metrik/10` bab 3): stockout <8% (rata-rata harian), waste <1.500 g dan <Rp50.000 per rumah tangga per bulan; ≥60% sinyal MENIPIS berujung pesan TitipO ≤48 jam; ≥50% batch SEGERA dipakai (bukan dibuang).
- **Kontrak bilateral `pedaree.stok.v1`** (Pedaree = PRODUSEN, TitipO = satu-satunya konsumen; KONTEKS §3.1): 3 jenis `stok.menipis`, `stok.habis`, `kedaluwarsa.dekat`; dedup produsen maks 1 sinyal per item per 24 jam (BR-301); payload wajib `item`, `sisa`, `satuan` (13 baku), `kedaluwarsa`, `recipe_id` Pawonee (boleh kosong); penerima TitipO `POST /sinyal/pedaree-stok` dengan header `X-Service-Key` (201 `dicatat_sebagai_anjuran`, duplikat 200 `duplikat_diabaikan`, kunci idempoten konsumen `item_id + tanggal`). Sifatnya **anjuran restock saja — TIDAK PERNAH membuat pesanan otomatis**; relevansi 48 jam.
- **Modul `:shared:pantry-resep`** (`id.chefgenie.pawonee:pantry-resep:1.0.0`) adalah milik **Pawonee**; Pedaree hanya mengonsumsi API publiknya dan dilarang mengubahnya.
- DB logis `pedaree` (DB per service); JWT akses 15 menit + refresh 7 hari (reuse-detection), audiens `pedaree`.
- Uang integer IDR; berat/volume gram/ml dengan pembulatan setengah ke atas 1 desimal; satuan hitung bilangan bulat; ID entitas ULID (`itm_`, `btc_`, `hh_`); waktu RFC3339 UTC, tanggal `YYYY-MM-DD`.
- Batas Varian 1: maks 400 PantryItem aktif dan 2.000 batch per rumah tangga; retensi MutasiStok 365 hari; unik `(householdId, lower(nama))` untuk item aktif.

## Ketidaksesuaian dokumen yang diketahui (jangan dijadikan fakta)

- `produk/30-modul-KMP-bersama.md` menyebut Pedaree sebagai pemilik modul dan koordinat `id.pedaree:pantry-resep`; KONTEKS §1 dan townhall-roadmap §2 menetapkan **Pawonee sebagai pemilik** (`id.chefgenie.pawonee:pantry-resep:1.0.0`). Repo ini mengikuti KONTEKS.
- BRD `10-inventori.md` BR-103 memuat daftar 13 satuan yang berbeda dari file inventori (mis. `g`, `ons`, `butir`, `pak`); sumber sah tetap `inventori/20-satuan-hortikultura.md`.
- `produk/20`/`produk/21` menyebut server Bun + Elysia, basis `https://api.pedaree.id/v1`, JWT 30 hari; keputusan terkunci adalah Rust + Axum 0.8, `https://api.pedaree.chefgenie.id/v1`, JWT akses 15 menit + refresh 7 hari. Repo ini mengikuti keputusan terkunci; perbaikan dokumen lewat PR di TownHall.
- `produk/20` bab 2.5 mencantumkan jenis sinyal `MENIPIS|HABIS` saja; kontrak bilateral mengunci 3 jenis (ditambah `kedaluwarsa.dekat`).

## Aturan kerja AI

1. **Baca dulu**: baca `AGENTS.md` ini dan semua ADR di `docs/decisions/` sebelum menulis kode.
2. **TDD merah-hijau**: tulis uji gagal dulu, lalu implementasi. Rilis diblokir bila QA gate gagal (SRS QA-001..QA-003).
3. **Kontrak berversi**: kontrak API/event hanya diubah lewat bump versi dan dicatat di ADR baru; event baru atau perubahan skema memakai masa dual-read 30 hari (KONTEKS §9).
4. **Commit & CHANGELOG**: awalan `docs:`/`feat:`/`fix:`; setiap commit yang mengubah perilaku wajib memperbarui `CHANGELOG.md` repo.
5. **ADR immutable**: keputusan arsitektur baru = tambah ADR bernomor di `docs/decisions/` (1 keputusan per file, berurutan). ADR lama tidak diedit; ganti dengan ADR baru berstatus "Menggantikan ADR-NNNN".
6. **Isolasi data**: DB per service. Dilarang menyentuh DB divisi lain; Pedaree hanya berbicara ke TitipO lewat kontrak `pedaree.stok.v1` dan ke Pawonee lewat modul `:shared:pantry-resep`/API-nya; Titeny hanya membaca (read-only) dari DB sumber.
7. **Tanpa duplikasi requirement**: requirement berubah = PR di `Pedaree-TownHall` dulu, baru kode mengikuti.
8. **Dokumen beku**: `versions/v1.0.0/` (termasuk `40-TECHSTACK.md` dan `60-BLAST-RADIUS.md`) tidak diedit; tambahan ditulis di `docs/ARSITEKTUR-AI-DEV.md`, perubahan besar masuk `v1.1.0`/`v2.0.0`.
9. **Sinyal ke TitipO = anjuran**: kode apa pun yang membuat pesanan TitipO otomatis dari stok dianggap cacat dan memblokir rilis.
10. **Idempoten**: setiap sinyal membawa `item_id` + `tanggal`; duplikat tidak boleh menggandakan efek; konsumen tercatat di ADR.
11. **Anjuran saja**: pipa tidak punya jalur yang membuat pesanan TitipO; hanya mengirim sinyal.

## Definisi selesai

Dari [townhall-roadmap §6](https://github.com/Coding-Skuy/ChefGenie-TownHall/blob/main/townhall-roadmap.md) (per milestone app):

- Dokumen versi lengkap (BRD/FRD/FSD/PRD/SRS) + `SNAPSHOT-ROADMAP.md`.
- QA gate berbasis SRS lulus (TDD merah-hijau).
- Kontrak API terbit; audit keamanan bersih (JWT audiens + DB per service).
- Bukti metrik lintas-divisi (KONTEKS §7) tercatat.
- CHANGELOG versi diperbarui; dokumen beku tidak diedit.

Khusus repo ini: sinyal 3 jenis terkirim ke `POST /sinyal/pedaree-stok` dengan dedup 24 jam, skema event `pedaree.stok.v1` tervalidasi, agregat stockout/waste sesuai rumus `metrik/10`.
